# Magic Formula in Brazil

Replication of Joel Greenblatt's Magic Formula in the Brazilian stock market, from 2009 to 2024, with the backtest, the results and the article.

**Article:** [Performance analysis of Greenblatt's Magic Formula in the Brazilian market](paper/magic_formula_brazil_revised_en.pdf). This is a revised English edition, and it opens with a note on what changed from the Portuguese version of 2025. The Portuguese originals are in [`paper/original_pt/`](paper/original_pt/).

The data collection and the construction of the signals are in the companion repository, [brazil-equity-factors](https://github.com/pedroandion/brazil-equity-factors).

## Results

All results are before transaction costs.

| Portfolio | CAGR | Volatility | Sharpe | Monthly alpha | Alpha p-value |
|---|---|---|---|---|---|
| **Magic Formula (24 stocks)** | **12.0%** | **22.0%** | **0.12** | **0.22%** | **30.6%** |
| 1st quintile | 13.9% | 23.6% | 0.19 | 0.29% | 22.6% |
| 5th quintile | 7.1% | 28.6% | -0.08 | 0.05% | 85.9% |
| Long-short, best 25% against worst 25% | 3.3% | 15.6% | 0.21 | 0.30% | 36.5% |
| Magic Formula + Net Debt/Ebit | 14.8% | 21.9% | 0.25 | 0.42% | 4.0% |
| Magic Formula + Momentum | 16.6% | 21.3% | 0.34 | 0.34% | 10.6% |
| Magic Formula + Low Vol | 10.7% | 19.4% | 0.07 | 0.10% | 55.9% |
| 1st quintile + Momentum | 19.6% | 23.2% | 0.44 | 0.49% | 3.3% |
| Ibovespa | 7.0% | 24.1% | -0.10 | -0.16% | 3.4% |
| CDI | 9.4% | - | - | - | - |

The Sharpe is (CAGR - CDI) / volatility for the Long portfolios and CAGR / volatility for the long-short one. The alpha comes from the Carhart four-factor model, with monthly returns and the NEFIN factors.

- **Return.** The Magic Formula beat the Ibovespa by about 5 percentage points per year. It did so in 10 of the 16 years, and in 65%, 68% and 92% of the rolling windows of 12, 36 and 60 months.
- **Alpha.** The alpha of the Magic Formula is positive, but not statistically significant, so the results do not establish abnormal returns. The same goes for the long-short portfolios.
- **Risk.** Volatility is lower than that of the Ibovespa, but the maximum drawdown is deeper (-55.1% against -48.6%), and the portfolio had 6 negative years, as many as the index.
- **Variations.** Only the Magic Formula with Net Debt/Ebit and the 1st quintile with Momentum have alphas significant at the 5% level, before any adjustment for the number of portfolios tested.

## Method

- **Universe.** Stocks in the SMLL and MLCX indices, using their historical composition, to reduce survivorship bias. The sectors labeled `Financeiro`, `Financeiro e Outros` and `Utilidade Pública` by the data provider are excluded. A stock must have a price and a median traded value above R$ 1 million over the last 42 days. When a company has several tickers, only the most liquid one counts.
- **Ranking.** Return on Capital is the EBIT of the last 12 months divided by net working capital plus net fixed assets, from the balance sheet of four quarters earlier. Earnings Yield is the same EBIT divided by market value plus net debt. A company with EBIT at or below zero, or without the data, leaves the ranking. The final rank is the sum of the two positions.
- **Portfolios.** A 24-stock portfolio that buys 6 stocks every three months and sells the oldest 6; five quintiles rebalanced monthly; and six long-short portfolios, also monthly, from 10% to 50% on each side. The Appendix of the article repeats them with Net Debt/Ebit, Momentum or Low Vol added to the ranking. All weights are equal.
- **Timing.** The signal is the one from the day before the rebalance, and the new weights earn returns from the next day on.

## Repository

| Location | Content |
|---|---|
| `magic_formula_backtests.ipynb` | The backtests, charts and tables |
| `magic_formula/` | The functions of the notebook: portfolio construction, weights, selection and backtest engine |
| `results/` | The tables that the notebook exports, which the article uses |
| `paper/` | The article in PDF and Word, and the Portuguese originals |
| `data/` | The market data and the three signals |

The last section of the notebook, `Numbers used in the article`, exports what the other tables do not show: the number of stocks per portfolio, the Ibovespa and the CDI in the window of the portfolios, the CAGR and Sharpe as the article reports them, and the rolling windows.

## Limitations

- **No costs.** Brokerage, stock lending and market impact are left out. They matter most for the long-short portfolios, whose alpha could disappear after stock lending costs.
- **Robustness.** Moving a few companies in or out of the sector filter moved the CAGR of the Magic Formula between 11.8% and 12.8% in the variations tested, because it shifts the rank of all the others. In those variations and in partial versions of the corrections, the alpha of the Magic Formula with Net Debt/Ebit fell to the 10% significance level.
- **Multiple tests.** The p-values are not adjusted for the number of portfolios tested.
- **Delistings.** A stock that stops trading keeps a zero return until the next rebalance.
- **Sector labels.** The provider's `Financeiro` label is broader than GICS Financials: it also holds real estate companies and some holding companies, while other holdings, such as Bradespar, are labeled as materials and stay in the universe.
- **Ranking edge cases.** Negative enterprise value (1.6% of the data) and negative capital with positive EBIT (0.5%) stay at the end of the ranking, although economically these are cheap or capital-light cases.
- **Price gaps.** The price file has gaps, and a gap of two days or more loses the return of that period. Filling all of them changes the CAGR of the article tables by at most 0.1 percentage point.
- **Sharpe ratio.** The `Sharpe` row in `results/statistics_*.csv` uses the mean excess return over the CDI. The article uses the definition above, exported in `results/article_performance.csv`.
- **Data vintages.** The price file comes from another collection than the one in the companion repository, so strategies with similar names report different numbers there.

## Data

Prices, volume, index composition and benchmarks come from [Comdinheiro](https://www.comdinheiro.com.br/), and the factor returns from [NEFIN-USP](https://nefin.com.br/). The signals `roc_mf`, `earnings_yield_mf` and `debt_ebit_mf` are built in the companion repository.

Raw financial statements and market values in R$ are licensed and are not in this repository. `relative_market_value.csv.gz` holds each stock's share of the day's total market value, which is enough for the market value weights.

## Running the notebook

The notebook was run with Python 3.13.

```bash
git clone https://github.com/pedroandion/magic-formula-brazil.git
cd magic-formula-brazil
python -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m nbconvert --to notebook --execute --inplace magic_formula_backtests.ipynb
```

It takes about 15 minutes on a laptop and rewrites the tables in `results/`. The workflow in `.github/workflows/run-notebooks.yml` runs it on a clean Linux machine.

## License

The code is under the [MIT License](LICENSE). The data files and the article are not covered by it: the data is included only so that the results can be reproduced, and it remains subject to the terms of its sources.

## Author

Pedro Andion de Oliveira Freitas
