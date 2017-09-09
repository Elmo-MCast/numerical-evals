from joblib import Parallel, delayed
import multiprocessing
import pandas as pd


class Network:
    def __init__(self, num_leafs=1056, num_hosts_per_leaf=48):
        self._num_cores = multiprocessing.cpu_count() - 1
        self.num_leafs = num_leafs
        self.num_hosts_per_leaf = num_hosts_per_leaf
        self.num_hosts = num_leafs * num_hosts_per_leaf

        self.leaf_to_hosts_map = None
        self._get_leaf_to_hosts_map()

        self.host_to_leaf_map = None
        self._get_host_to_leaf_map()

    def _get_leaf_to_hosts_map_0(self, l):
        return pd.Series([(l * self.num_hosts_per_leaf) + h
                          for h in range(self.num_hosts_per_leaf)])

    def _get_leaf_to_hosts_map(self):
        self.leaf_to_hosts_map = Parallel(n_jobs=self._num_cores)(delayed(self._get_leaf_to_hosts_map_0)(l)
                                                                  for l in range(self.num_leafs))

    def _get_host_to_leaf_map(self):
        host_to_leaf_list = []
        for l in range(self.num_leafs):
            host_to_leaf_list += [l for _ in range(self.num_hosts_per_leaf)]
        self.host_to_leaf_map = pd.Series(host_to_leaf_list)


if __name__ == "__main__":
    t_network = Network(48, 48)

    print(t_network.leaf_to_hosts_map)
