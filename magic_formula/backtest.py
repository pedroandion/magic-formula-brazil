"""Backtests of the Magic Formula portfolio, the quintiles and the long-short portfolios."""
import numpy as np
import pandas as pd

from .portfolio import magic_formula_portfolio
from .weights import compute_directional_weights, compute_longshort_weights, compute_weights


def adjust_position(weights, date_index, portfolios_by_date, rebalance_dates):
    
    if date_index == 0:
        pass
    
    elif date_index == 1:
        weights = weights.div(2)

    elif date_index == 2:
        old_stocks = portfolios_by_date[rebalance_dates[date_index - 2]] + portfolios_by_date[rebalance_dates[date_index - 1]]
        new_stocks = portfolios_by_date[rebalance_dates[date_index]]

        weights.loc[old_stocks] = weights.loc[old_stocks].mul(2/3)
        weights.loc[new_stocks] = weights.loc[new_stocks].mul(1/3)

    elif date_index == 3:
        old_stocks = portfolios_by_date[rebalance_dates[date_index - 3]] + portfolios_by_date[rebalance_dates[date_index - 2]] + portfolios_by_date[rebalance_dates[date_index - 1]]
        new_stocks = portfolios_by_date[rebalance_dates[date_index]]

        weights.loc[old_stocks] = weights.loc[old_stocks].mul(3/4)
        weights.loc[new_stocks] = weights.loc[new_stocks].mul(1/4)

    else:
        old_stocks = portfolios_by_date[rebalance_dates[date_index - 3]] + portfolios_by_date[rebalance_dates[date_index - 2]] + portfolios_by_date[rebalance_dates[date_index - 1]]
        new_stocks = portfolios_by_date[rebalance_dates[date_index]]
        
        adjustment = 0.75 / weights.loc[old_stocks].sum()

        weights.loc[old_stocks] = weights.loc[old_stocks].mul(adjustment)
        weights.loc[new_stocks] = weights.loc[new_stocks].div(4)

    return weights

def backtest(df_prices: pd.DataFrame, portfolios_by_date, trade_dates, market_value: pd.DataFrame, weight_type: str, multiple_portfolios: bool = False)-> pd.DataFrame:
    # Calculates the return of a stock portfolio over time

    # Creates a dataframe with the percentage price changes of each stock
    prices_pct = df_prices.pct_change(fill_method = 'ffill', limit = 1).fillna(0)

    # Dates used in the simulation
    backtest_dates = prices_pct.loc[trade_dates[0]:].index

    # Series and Dataframe that store the strategy's daily returns and each asset's weight at the start of the day, respectively
    daily_return = pd.Series(index = prices_pct.index, name = 'Daily return')
    daily_weights = pd.DataFrame(index = prices_pct.index, columns = prices_pct.columns)

    
    # Calculates the total portfolio returns as separate portfolios, assets are not rebalanced within a portfolio, only between portfolios
    if multiple_portfolios:
        for dt0 in backtest_dates[:-1]:
            date_location = backtest_dates.get_loc(dt0)
            dt1 = backtest_dates[date_location + 1]

            if dt0 in trade_dates:
                
                daily_return.loc[dt0] = (daily_weights.loc[dt0] * (prices_pct.loc[dt0])).sum()
                daily_weights.loc[dt1] = (daily_weights.loc[dt0] * (1 + prices_pct.loc[dt0])) / (1 + daily_return.loc[dt0])
                dtm1 = prices_pct.index[prices_pct.index.get_loc(dt0) - 1]
                daily_weights.loc[dt1, portfolios_by_date[dt0]] = compute_weights(portfolios_by_date[dt0], dtm1, market_value, weight_type)
                i = trade_dates.index(dt0)
                if i- 4 >= 0:
                    removed_stocks = [item for item in portfolios_by_date[trade_dates[i - 4]] if item not in portfolios_by_date[dt0]]
                    daily_weights.loc[dt1, removed_stocks] = np.nan

                daily_weights.loc[dt1] = adjust_position(daily_weights.loc[dt1], i, portfolios_by_date, trade_dates)

            else:

                daily_return.loc[dt0] = (daily_weights.loc[dt0] * (prices_pct.loc[dt0])).sum()
                daily_weights.loc[dt1] = (daily_weights.loc[dt0] * (1 + prices_pct.loc[dt0])) / (1 + daily_return.loc[dt0])

        daily_return.loc[dt1] = (daily_weights.loc[dt1] * (prices_pct.loc[dt1])).sum()

    # Calculates the total portfolio returns as a single portfolio, rebalancing all assets on the rebalancing date
    else:

        for dt0 in backtest_dates[:-1]:
            date_location = backtest_dates.get_loc(dt0)
            dt1 = backtest_dates[date_location + 1]

            if dt0 in trade_dates:

                daily_return.loc[dt0] = (daily_weights.loc[dt0] * (prices_pct.loc[dt0])).sum()
                dtm1 = prices_pct.index[prices_pct.index.get_loc(dt0) - 1]
                daily_weights.loc[dt1, portfolios_by_date[dt0]] = compute_weights(portfolios_by_date[dt0], dtm1, market_value, weight_type)

            else:

                daily_return.loc[dt0] = (daily_weights.loc[dt0] * (prices_pct.loc[dt0])).sum()
                daily_weights.loc[dt1] = (daily_weights.loc[dt0] * (1 + prices_pct.loc[dt0])) / (1 + daily_return.loc[dt0])

        daily_return.loc[dt1] = (daily_weights.loc[dt1] * (prices_pct.loc[dt1])).sum()

    return daily_return

def backtest_total(rebalance_dates: list, final_rank: pd.DataFrame, df_prices: pd.DataFrame, market_value: pd.DataFrame, portfolio_size: int, buy_size: int, weight_type: str, multiple_portfolios:bool = False)-> pd.DataFrame:
    # Calculates the return of the Long portfolio

    # Parameter in magic_formula_portfolio that defines whether the function returns only the new stocks added on the date
    # This parameter is needed to calculate the return of simultaneous portfolios
    new_stocks = True if multiple_portfolios else False 

    # Returns the Long portfolio
    long_portfolio = magic_formula_portfolio(rebalance_dates, final_rank, portfolio_size, buy_size, new_stocks_only = new_stocks)
    
    # Calculates the returns of the Long portfolio
    long_returns = backtest(df_prices, long_portfolio, rebalance_dates, market_value, weight_type, multiple_portfolios)

    port_type = 'multiple' if multiple_portfolios else 'single'

    long_returns.name = 'long_' + weight_type + '_' + port_type
    long_returns.index = pd.to_datetime(long_returns.index)

    return long_returns

def backtest_quintiles(df_prices, quintile, trade_dates, market_value):
    # Calculates the return of a stock portfolio over time

    # Creates a dataframe with the percentage price changes of each stock
    prices_pct = df_prices.pct_change(fill_method = 'ffill', limit = 1).fillna(0)
    backtest_dates = prices_pct.loc[trade_dates[0]:].index

    daily_return = pd.Series(index = prices_pct.index, name = 'Daily return')
    return_by_stock = pd.DataFrame(index = prices_pct.index, columns = prices_pct.columns)
    daily_weights = pd.DataFrame(index = prices_pct.index, columns = prices_pct.columns)
    
    for dt0 in backtest_dates[:-1]:
        date_location = backtest_dates.get_loc(dt0)
        dt1 = backtest_dates[date_location + 1]

        if dt0 in trade_dates:

            return_by_stock.loc[dt0] = (daily_weights.loc[dt0] * (prices_pct.loc[dt0]))
            daily_return.loc[dt0] = return_by_stock.loc[dt0].sum()
            dtm1 = prices_pct.index[prices_pct.index.get_loc(dt0) - 1]
            daily_weights.loc[dt1] = compute_directional_weights(quintile.loc[dtm1], dtm1, market_value, weight_type = 'equal')

        else:

            return_by_stock.loc[dt0] = (daily_weights.loc[dt0] * (prices_pct.loc[dt0]))
            daily_return.loc[dt0] = return_by_stock.loc[dt0].sum()
            daily_weights.loc[dt1] = (daily_weights.loc[dt0] * (1 + prices_pct.loc[dt0])) / (1 + daily_return.loc[dt0])

    return_by_stock.loc[dt1] = (daily_weights.loc[dt1] * (prices_pct.loc[dt1]))
    daily_return.loc[dt1] = return_by_stock.loc[dt1].sum()

    return daily_return

def backtest_longshort(df_prices, short_sig, long_sig, trade_dates, market_value):
    # Calculates the return of a stock portfolio over time

    # Creates a dataframe with the percentage price changes of each stock
    prices_pct = df_prices.pct_change(fill_method = 'ffill', limit = 1).fillna(0)
    backtest_dates = prices_pct.loc[trade_dates[0]:].index

    daily_return = pd.Series(index = prices_pct.index, name = 'Daily return')
    return_by_stock = pd.DataFrame(index = prices_pct.index, columns = prices_pct.columns)
    daily_weights = pd.DataFrame(index = prices_pct.index, columns = prices_pct.columns)
    
    for dt0 in backtest_dates[:-1]:
        date_location = backtest_dates.get_loc(dt0)
        dt1 = backtest_dates[date_location + 1]

        if dt0 in trade_dates:

            return_by_stock.loc[dt0] = (daily_weights.loc[dt0] * (prices_pct.loc[dt0]))
            daily_return.loc[dt0] = return_by_stock.loc[dt0].sum()
            dtm1 = prices_pct.index[prices_pct.index.get_loc(dt0) - 1]
            daily_weights.loc[dt1] = compute_longshort_weights(short_sig.loc[dtm1], long_sig.loc[dtm1], dtm1, market_value, weight_type = 'equal')

        else:

            return_by_stock.loc[dt0] = (daily_weights.loc[dt0] * (prices_pct.loc[dt0]))
            daily_return.loc[dt0] = return_by_stock.loc[dt0].sum()
            daily_weights.loc[dt1] = (daily_weights.loc[dt0] * (1 + prices_pct.loc[dt0])) / (1 + daily_return.loc[dt0])

    return_by_stock.loc[dt1] = (daily_weights.loc[dt1] * (prices_pct.loc[dt1]))
    daily_return.loc[dt1] = return_by_stock.loc[dt1].sum() 

    return daily_return
