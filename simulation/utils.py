import progressbar
from cffi import FFI
import json
import pickle
import marshal

ffi = FFI()


def bar_range(x, desc):
    widgets = [
        '%s: ' % desc, progressbar.Percentage(),
        ' ', progressbar.Bar(),
        ' ', progressbar.ETA(),
    ]
    bar = progressbar.ProgressBar(widgets=widgets)
    if isinstance(x, range) or isinstance(x, list):
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


def pickle_dump_obj(o, f):
    _f = open(f, 'wb')
    pickle.dump(o, _f, protocol=pickle.HIGHEST_PROTOCOL)
    _f.close()


def pickle_load_obj(f):
    _f = open(f, 'rb')
    o = pickle.load(_f)
    _f.close()
    return o


def json_dump_obj(o, f):
    _f = open(f, 'w')
    json.dump(o, _f)
    _f.close()


def json_load_obj(f):
    _f = open(f, 'r')
    o = json.load(_f)
    _f.close()
    return o


def marshal_dump_obj(o, f):
    _f = open(f, 'wb')
    marshal.dump(o, _f, 4)
    _f.close()


def marshal_load_obj(f):
    _f = open(f, 'rb')
    o = marshal.load(_f)
    _f.close()
    return o

