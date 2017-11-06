import numpy as np
import pandas as pd
import progressbar
from cffi import FFI
import pickle

ffi = FFI()


def bar_range(x, desc):
    widgets = [
        '%s: ' % desc, progressbar.Percentage(),
        ' ', progressbar.Bar(),
        ' ', progressbar.ETA(),
    ]
    bar = progressbar.ProgressBar(widgets=widgets)
    if isinstance(x, range):
        return bar(x)
    else:
        return bar(range(x))


ffi.cdef("""
uint64_t popcount(uint64_t x);
""")

C = ffi.verify("""
#include <stdint.h>

uint64_t popcount(uint64_t x) {
    return __builtin_popcountll(x);
}
""")


def popcount(x):
    return C.popcount(x)


def dump_obj(o, f):
    _f = open(f, 'wb')
    pickle.dump(o, _f)
    _f.close()


def load_obj(f):
    _f = open(f, 'rb')
    o = pickle.load(_f)
    _f.close()
    return o


# def ecdf(sample):
#     # convert sample to a numpy array, if it isn't already
#     sample = np.atleast_1d(sample)
#
#     # find the unique values and their corresponding counts
#     quantiles, counts = np.unique(sample, return_counts=True)
#
#     # take the cumulative sum of the counts and divide by the sample size to
#     # get the cumulative probabilities between 0 and 1
#     cumprob = np.cumsum(counts).astype(np.double) / sample.size
#
#     return quantiles, cumprob
#
#
# def plot_ecdf(sample, x_title='p', y_title='q'):
#     q, p = ecdf(sample)
#
#     df = pd.DataFrame()
#     df[x_title] = q
#     df[y_title] = p
#
#     sb.factorplot(x=x_title, y=y_title, data=df)
