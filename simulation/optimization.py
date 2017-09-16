from simulation import algorithms


class Optimization:
    def __init__(self, data):
        self.data = data
        self.network = self.data['network']
        self.network_maps = self.network['maps']
        self.tenants = self.data['tenants']
        self.tenants_maps = self.tenants['maps']
        self.placement = self.data['placement']
        self.placement['maps'] = {'leafs_to_rules_count': {l: 0 for l in range(self.network['num_leafs'])}}

        self._optimize()

        print('optimization: complete.')

    def _optimize(self):
        for t in range(self.tenants['num_tenants']):
            for g in range(self.tenants_maps[t]['group_count']):
                if self.tenants_maps[t]['groups_map'][g]['leaf_count'] > self.placement['num_bitmaps']:
                    algorithms.run(
                        data=self.tenants_maps[t]['groups_map'][g],
                        max_bitmaps=self.placement['num_bitmaps'],
                        leafs_to_rules_count_map=self.placement['maps']['leafs_to_rules_count'],
                        max_rules_perf_leaf=self.network['num_rules_per_leaf'],
                        num_hosts_per_leaf=self.network['num_hosts_per_leaf'])
