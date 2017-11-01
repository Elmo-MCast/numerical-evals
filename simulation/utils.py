import numpy as np
import pandas as pd
import seaborn as sb
from tqdm import trange, tnrange

try:
    get_ipython


    def bar_range(x, desc):
        return tnrange(x, desc=desc)
except:
    def bar_range(x, desc):
        return trange(x, desc=desc)


def ecdf(sample):
    # convert sample to a numpy array, if it isn't already
    sample = np.atleast_1d(sample)

    # find the unique values and their corresponding counts
    quantiles, counts = np.unique(sample, return_counts=True)

    # take the cumulative sum of the counts and divide by the sample size to
    # get the cumulative probabilities between 0 and 1
    cumprob = np.cumsum(counts).astype(np.double) / sample.size

    return quantiles, cumprob


def plot_ecdf(sample, x_title='p', y_title='q'):
    q, p = ecdf(sample)

    df = pd.DataFrame()
    df[x_title] = q
    df[y_title] = p

    sb.factorplot(x=x_title, y=y_title, data=df)
