from threading import Thread
import operator
from functools import reduce
import pandas as pd


class Network:
    def __init__(self, num_leafs=1056, num_hosts_per_leaf=48, multi_threaded=True, num_threads=2):
        self.num_leafs = num_leafs
        self.num_hosts_per_leaf = num_hosts_per_leaf
        self.num_hosts = num_leafs * num_hosts_per_leaf
        self.multi_threaded = multi_threaded
        self.num_threads = num_threads

        if self.multi_threaded:
            self.num_chunks = self.num_threads
            if self.num_leafs % self.num_chunks != 0:
                raise Exception("number of threads should be a multiple of leafs count")
            self.chunk_size = int(self.num_leafs / self.num_chunks)

            # print('network: no. of chunks %s' % self.num_chunks)

        self.leaf_to_hosts_map = None
        self._get_leaf_to_hosts_map()

        self.host_to_leaf_map = None
        self._get_host_to_leaf_map()

        print('network: initialized.')

    def _get_leaf_to_hosts_map_chunk(self, leaf_to_hosts_map_chunks, chunk_id, chunk_size):
        base_index = chunk_id * chunk_size
        leaf_to_hosts_map = [None] * chunk_size

        for l in range(base_index, base_index + chunk_size):
            leaf_to_hosts_map[l % chunk_size] = pd.Series([(l * self.num_hosts_per_leaf) + h
                                                           for h in range(self.num_hosts_per_leaf)])
        leaf_to_hosts_map_chunks[chunk_id] = leaf_to_hosts_map

    def _get_leaf_to_hosts_map(self):
        if not self.multi_threaded:
            self.leaf_to_hosts_map = [None] * self.num_leafs

            for l in range(self.num_leafs):
                self.leaf_to_hosts_map[l] = pd.Series([(l * self.num_hosts_per_leaf) + h
                                                       for h in range(self.num_hosts_per_leaf)])
        else:
            leaf_to_hosts_map_chunks = [None] * self.num_chunks
            leaf_to_hosts_map_threads = [None] * self.num_chunks

            for i in range(self.num_chunks):
                leaf_to_hosts_map_threads[i] = Thread(target=self._get_leaf_to_hosts_map_chunk,
                                                      args=(leaf_to_hosts_map_chunks, i, self.chunk_size))
                leaf_to_hosts_map_threads[i].start()

            for i in range(self.num_chunks):
                leaf_to_hosts_map_threads[i].join()

            self.leaf_to_hosts_map = reduce(operator.concat, leaf_to_hosts_map_chunks)

    def _get_host_to_leaf_map(self):
        host_to_leaf_list = []
        for l in range(self.num_leafs):
            host_to_leaf_list += [l for _ in range(self.num_hosts_per_leaf)]
        self.host_to_leaf_map = pd.Series(host_to_leaf_list)


if __name__ == "__main__":
    t_network = Network(48, 48)

    print(t_network.leaf_to_hosts_map)
