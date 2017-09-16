from simulation import algorithms


class Optimization:
    def __init__(self, data, use_all_bitmaps=False, use_default_bitmap=False):
        self.data = data
        self.network = self.data['network']
        self.network_maps = self.network['maps']
        self.tenants = self.data['tenants']
        self.tenants_maps = self.tenants['maps']
        self.placement = self.data['placement']
        self.placement['maps'] = {'leafs_to_rules_count': {l: 0 for l in range(self.network['num_leafs'])}}
        self.use_default_bitmap = use_default_bitmap
        self.use_all_bitmaps = use_all_bitmaps

        self._optimize()

        print('optimization: complete.')

    def _optimize(self):
        for t in range(self.tenants['num_tenants']):
            for g in range(self.tenants_maps[t]['group_count']):
                if self.tenants_maps[t]['groups_map'][g]['leaf_count'] > self.placement['num_bitmaps']:
                    algorithms.dynmaic(
                        data=self.tenants_maps[t]['groups_map'][g],
                        max_bitmaps=self.placement['num_bitmaps'],
                        leafs_to_rules_count_map=self.placement['maps']['leafs_to_rules_count'],
                        max_rules_perf_leaf=self.network['num_rules_per_leaf'],
                        use_all_bitmaps=self.use_all_bitmaps,
                        use_default_bitmap=self.use_default_bitmap)
