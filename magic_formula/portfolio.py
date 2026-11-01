"""Builds the Magic Formula portfolio on each rebalancing date."""
from datetime import timedelta

from bizdays import Calendar, set_option

cal = Calendar.load('ANBIMA')
set_option('mode', 'pandas')


def magic_formula_portfolio(trade_dates, stocks_rank, portfolio_size, buy_size, bottom = False, new_stocks_only = False):
    # Builds the full portfolio for the whole backtest period
    # The function can return a dictionary with the full set of assets or only the new companies per date
    portfolio = list()
    portfolio_on_date = dict()

    # Collects, per rebalancing date, the new stocks that will make up the portfolio
    for dt in trade_dates:
        # Filters the rank on a date
        dt_ref = cal.preceding(dt - timedelta(days = 1))
        stocks = stocks_rank.loc[dt_ref].dropna()
        
        # Sorts the values according to the parameters, if bottom = True returns the worst in the rank
        stocks = stocks.sort_values(ascending = False) if bottom else stocks.sort_values()

        # If the portfolio has not reached the maximum size, the function just adds more stocks to the final portfolio
        if len(portfolio) < portfolio_size:
            # Adds new stocks besides those already in the portfolio
            stocks_to_buy = stocks.loc[~stocks.index.isin(portfolio)].head(buy_size).index
            portfolio.extend(stocks_to_buy.tolist()) # extend "adds up" two lists
        else:
        # After reaching the full size, the function removes the first n stocks in the portfolio and adds n new ones
        # A stock can return to the portfolio as long as it is cheap, so we remove stocks before filtering the new ones.
            portfolio = portfolio[buy_size:]
            stocks_to_buy = stocks.loc[~stocks.index.isin(portfolio)].head(buy_size).index
            portfolio.extend(stocks_to_buy.tolist())

        # Conditional on the new_stocks_only variable: if you only want the stocks added on the date, set it to True
        # new_stocks_only = False returns the full portfolio for the date
        portfolio_on_date[dt] = stocks_to_buy.tolist() if new_stocks_only else portfolio.copy()

    return portfolio_on_date
