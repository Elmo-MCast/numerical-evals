import pandas as pd


class Network:
    def __init__(self, num_leafs=1056, num_hosts_per_leaf=48):
        self.num_leafs = num_leafs
        self.num_hosts_per_leaf = num_hosts_per_leaf
        self.num_hosts = num_leafs * num_hosts_per_leaf

        self.leaf_to_host_map = None
        self._get_leaf_to_host_map()

        self.host_to_leaf_map = None
        self._get_host_to_leaf_map()

    def _get_leaf_to_host_map(self):
        self.leaf_to_host_map = [None] * self.num_leafs

        for i in range(self.num_leafs):
            self.leaf_to_host_map[i] = pd.Series([(i * self.num_hosts_per_leaf) + j
                                                  for j in range(self.num_hosts_per_leaf)])

    def _get_host_to_leaf_map(self):
        host_to_leaf_list = []
        for i in range(self.num_leafs):
            host_to_leaf_list += [i for _ in range(self.num_hosts_per_leaf)]
        self.host_to_leaf_map = pd.Series(host_to_leaf_list)
