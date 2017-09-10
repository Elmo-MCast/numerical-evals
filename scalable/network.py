from multiprocessing import Pool
import operator
from functools import reduce
import pandas as pd


def _get_leaf_to_hosts_map_chunk(num_hosts_per_leaf, chunk_id, chunk_size):
    base_index = chunk_id * chunk_size
    _leaf_to_hosts_map = [None] * chunk_size

    for l in range(base_index, base_index + chunk_size):
        _leaf_to_hosts_map[l % chunk_size] = pd.Series([(l * num_hosts_per_leaf) + h
                                                        for h in range(num_hosts_per_leaf)])
    return _leaf_to_hosts_map


def _get_leaf_to_hosts_map(multi_threaded, num_leafs, num_hosts_per_leaf,
                           num_chunks, chunk_size):
    if not multi_threaded:
        _leaf_to_hosts_map = [None] * num_leafs

        for l in range(num_leafs):
            _leaf_to_hosts_map[l] = pd.Series([(l * num_hosts_per_leaf) + h
                                               for h in range(num_hosts_per_leaf)])
    else:
        leaf_to_hosts_map_pool = Pool(processes=num_chunks)

        leaf_to_hosts_map_results = leaf_to_hosts_map_pool.starmap(_get_leaf_to_hosts_map_chunk,
                                                                   [(num_hosts_per_leaf, i, chunk_size)
                                                                    for i in range(num_chunks)])

        _leaf_to_hosts_map = reduce(operator.concat, leaf_to_hosts_map_results)

    return _leaf_to_hosts_map


def _get_host_to_leaf_map(num_leafs, num_hosts_per_leaf):
    host_to_leaf_list = []

    for l in range(num_leafs):
        host_to_leaf_list += [l for _ in range(num_hosts_per_leaf)]

    return pd.Series(host_to_leaf_list)


def initialize(num_leafs=1056, num_hosts_per_leaf=48, multi_threaded=True, num_threads=2):
    if multi_threaded:
        num_chunks = num_threads
        if num_leafs % num_chunks != 0:
            raise Exception("number of threads should be a multiple of leafs count")
        chunk_size = int(num_leafs / num_chunks)

        # print('network: no. of chunks %s' % self.num_chunks)
    else:
        num_chunks = 0
        chunk_size = 0

    _leaf_to_hosts_map = _get_leaf_to_hosts_map(multi_threaded, num_leafs, num_hosts_per_leaf,
                                                num_chunks, chunk_size)

    _host_to_leaf_map = _get_host_to_leaf_map(num_leafs, num_hosts_per_leaf)

    print('network: initialized.')

    return {'leaf_to_hosts_map': _leaf_to_hosts_map,
            'host_to_leaf_map': _host_to_leaf_map,
            'num_leafs': num_leafs,
            'num_hosts_per_leaf': num_hosts_per_leaf,
            'num_hosts': (num_leafs * num_hosts_per_leaf)}


if __name__ == "__main__":
    o_network = initialize(48, 48, num_threads=8)

    print(o_network['leaf_to_hosts_map'])
