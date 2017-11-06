from simulation.utils import bar_range, bar_tqdm
import numpy as np


class Network:
    def __init__(self, data, num_leafs=1056, num_hosts_per_leaf=48, num_rules_per_leaf=10000):
        self.data = data
        self.num_leafs = num_leafs
        self.num_hosts_per_leaf = num_hosts_per_leaf
        self.num_hosts = num_leafs * num_hosts_per_leaf

        self.data['network'] = {'num_leafs': self.num_leafs,
                                'num_hosts_per_leaf': self.num_hosts_per_leaf,
                                'num_hosts': self.num_hosts,
                                'num_rules_per_leaf': num_rules_per_leaf,
                                'maps': {
                                    'leaf_to_hosts': None,
                                    'host_to_leaf': None
                                }}

        self.network = self.data['network']
        self.network_maps = self.network['maps']

        self._get_leaf_to_hosts_map()
        print('network:leaf->hosts ... done')

        self._get_host_to_leaf_map()
        print('network:host->leaf ... done')

    def _get_leaf_to_hosts_map(self):
        _leaf_to_hosts_map = np.empty(shape=(self.num_leafs, self.num_hosts_per_leaf), dtype=int)

        _leaf_to_hosts_map[0, :] = np.array(range(self.num_hosts_per_leaf))
        for l in range(1, self.num_leafs):
            _leaf_to_hosts_map[l, :] = _leaf_to_hosts_map[l - 1, :] + self.num_hosts_per_leaf

        self.network_maps['leaf_to_hosts'] = _leaf_to_hosts_map

    def _get_host_to_leaf_map(self):
        _host_to_leaf_map = np.empty(shape=self.num_hosts, dtype=int)

        for l in range(self.num_leafs):
            i = l * self.num_hosts_per_leaf
            _host_to_leaf_map[i:i + self.num_hosts_per_leaf] = l

        self.network_maps['host_to_leaf'] = _host_to_leaf_map
