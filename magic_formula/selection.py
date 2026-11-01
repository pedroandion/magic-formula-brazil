"""Stock selection from a ranking: quintiles and long-short percentiles."""
import numpy as np
import pandas as pd


def get_quintiles(lower, upper, value_df):
    # Returns the investable companies based on the percentile given in the parameters

    # Calculates the lower and upper bounds of a quintile
    bottom = value_df.quantile(lower, axis = 1)
    top = value_df.quantile(upper, axis = 1)

    if lower == 0:
        value_df = value_df.apply(lambda col: np.where((col >= bottom) & (col <= top), 1, np.nan))
    else:
        value_df = value_df.apply(lambda col: np.where((col > bottom) & (col <= top), 1, np.nan))

    return value_df

def get_longshort(percentile, value_df, use_filter = False, filter_signal = None, filter_percentile = None):
    # Returns the investable companies based on the percentile given in the parameters

    if use_filter:
        filter_cut = filter_signal.quantile(filter_percentile, axis = 1)

        higher = filter_signal.apply(lambda col: np.where(col >= filter_cut, 1, np.nan))
        lesser = filter_signal.apply(lambda col: np.where(col < filter_cut, 1, np.nan))

        higher_bottom = (value_df * higher).quantile(percentile, axis = 1)
        higher_top = (value_df * higher).quantile(1 - percentile, axis = 1)
        lesser_bottom = (value_df * lesser).quantile(percentile, axis = 1)
        lesser_top = (value_df * lesser).quantile(1 - percentile, axis = 1)

        higher_short = (value_df * higher).apply(lambda col: np.where(col <= higher_bottom, 1, 0))
        higher_long = (value_df * higher).apply(lambda col: np.where(col >= higher_top, 1, 0))
        lesser_short = (value_df * lesser).apply(lambda col: np.where(col <= lesser_bottom, 1, 0))
        lesser_long = (value_df * lesser).apply(lambda col: np.where(col >= lesser_top, 1, 0))

        return higher_short, higher_long, lesser_short, lesser_long

    else:
        # Calculates the lower and upper bounds of a quintile
        bottom = value_df.quantile(percentile, axis = 1)
        top = value_df.quantile(1 - percentile, axis = 1)

        short = value_df.apply(lambda col: np.where(col <= bottom, 1, 0))
        long = value_df.apply(lambda col: np.where(col >= top, 1, 0))


        return short, long
