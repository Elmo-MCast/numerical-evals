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
        print('network[leaf_to_hosts]: initialized.')

        self._get_host_to_leaf_map()
        print('network[host_to_leaf]: initialized.')

    def _get_leaf_to_hosts_map(self):
        self.network_maps['leaf_to_hosts'] = [None] * self.num_leafs

        for l in range(self.num_leafs):
            self.network_maps['leaf_to_hosts'][l] = [(l * self.num_hosts_per_leaf) + h
                                                     for h in range(self.num_hosts_per_leaf)]

    def _get_host_to_leaf_map(self):
        self.network_maps['host_to_leaf'] = []
        for l in range(self.num_leafs):
            self.network_maps['host_to_leaf'] += [l for _ in range(self.num_hosts_per_leaf)]


if __name__ == "__main__":
    data = dict()

    Network(data, 48, 48)

    print(data)
