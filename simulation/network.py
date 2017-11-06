from simulation.utils import bar_range


class Network:
    def __init__(self, data, num_leafs=1056, num_hosts_per_leaf=48, num_rules_per_leaf=10000):
        self.data = data
        self.num_leafs = num_leafs
        self.num_hosts_per_leaf = num_hosts_per_leaf

        self.data['network'] = {'num_leafs': num_leafs,
                                'num_hosts_per_leaf': num_hosts_per_leaf,
                                'num_hosts': num_leafs * num_hosts_per_leaf,
                                'num_rules_per_leaf': num_rules_per_leaf,
                                'maps': {
                                    'leaf_to_hosts': None,
                                    'host_to_leaf': None
                                }}

        self.network = self.data['network']
        self.network_maps = self.network['maps']

        self._get_leaf_to_hosts_map()

        self._get_host_to_leaf_map()

    def _get_leaf_to_hosts_map(self):
        self.network_maps['leaf_to_hosts'] = [None] * self.num_leafs
        _leaf_to_hosts = self.network_maps['leaf_to_hosts']

        for l in bar_range(self.num_leafs, desc='network:leaf->hosts'):
            _leaf_to_hosts[l] = [(l * self.num_hosts_per_leaf) + h
                                 for h in range(self.num_hosts_per_leaf)]

    def _get_host_to_leaf_map(self):
        _host_to_leaf = []
        for l in bar_range(self.num_leafs, desc='network:host->leaf'):
            _host_to_leaf += [l for _ in range(self.num_hosts_per_leaf)]
        self.network_maps['host_to_leaf'] = _host_to_leaf

