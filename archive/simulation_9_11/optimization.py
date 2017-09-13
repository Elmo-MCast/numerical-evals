from simulation import algorithms


class Optimization:
    def __init__(self, data, post_process=False):
        self.data = data
        self.network = self.data['network']
        self.network_maps = self.network['maps']
        self.tenants = self.data['tenants']
        self.tenants_maps = self.tenants['maps']
        self.placement = self.data['placement']
        self.post_process = post_process

        self._optimize()

        print('optimization: complete.')

    def _optimize(self):
        for t in range(self.tenants['num_tenants']):
            for g in range(self.tenants_maps[t]['group_count']):
                if self.tenants_maps[t]['groups_map'][g]['leaf_count'] > self.placement['num_bitmaps']:
                    algorithms.dynmaic(
                        data=self.tenants_maps[t]['groups_map'][g],
                        max_bitmaps=self.placement['num_bitmaps'],
                        use_all_bitmaps=self.post_process)
