import numpy as np
from simulation import algorithms


class Optimization:
    def __init__(self, data, max_batch_size=1):
        self.data = data
        self.max_batch_size = max_batch_size

        self.network = self.data['network']
        self.network_maps = self.network['maps']
        self.tenants = self.data['tenants']
        self.tenants_maps = self.tenants['maps']
        self.placement = self.data['placement']
        self.placement['maps'] = {'leafs_to_rules_count': {l: 0 for l in range(self.network['num_leafs'])}}

        self.data['optimization'] = {'max_batch_size': max_batch_size}

        self._optimize()

        print('optimization: complete.')

    def _optimize(self):
        if self.max_batch_size <= 1:
            for t in range(self.tenants['num_tenants']):
                for g in range(self.tenants_maps[t]['group_count']):
                    if self.tenants_maps[t]['groups_map'][g]['leaf_count'] > self.placement['num_bitmaps']:
                        algorithms.run(
                            data=self.tenants_maps[t]['groups_map'][g],
                            max_bitmaps=self.placement['num_bitmaps'],
                            leafs_to_rules_count_map=self.placement['maps']['leafs_to_rules_count'],
                            max_rules_perf_leaf=self.network['num_rules_per_leaf'],
                            num_hosts_per_leaf=self.network['num_hosts_per_leaf'])
        else:
            batch_size = np.random.randint(low=1, high=self.max_batch_size + 1, size=1)[0]
            running_batch_size = 0
            running_batch_list = []

            for t in range(self.tenants['num_tenants']):
                for g in range(self.tenants_maps[t]['group_count']):
                    running_batch_list += [self.tenants_maps[t]['groups_map'][g]]
                    running_batch_size += 1

                    if running_batch_size == batch_size:
                        running_batch_list = sorted(running_batch_list, key=lambda item: item['leaf_count'])

                        for _g in running_batch_list:
                            if _g['leaf_count'] > self.placement['num_bitmaps']:
                                algorithms.run(
                                    data=_g,
                                    max_bitmaps=self.placement['num_bitmaps'],
                                    leafs_to_rules_count_map=self.placement['maps']['leafs_to_rules_count'],
                                    max_rules_perf_leaf=self.network['num_rules_per_leaf'],
                                    num_hosts_per_leaf=self.network['num_hosts_per_leaf'])

                        batch_size = np.random.randint(low=1, high=self.max_batch_size + 1, size=1)[0]
                        running_batch_size = 0
                        running_batch_list = []

                if (t + 1) == self.tenants['num_tenants']:
                    running_batch_list = sorted(running_batch_list, key=lambda item: item['leaf_count'])

                    for _g in running_batch_list:
                        if _g['leaf_count'] > self.placement['num_bitmaps']:
                            algorithms.run(
                                data=_g,
                                max_bitmaps=self.placement['num_bitmaps'],
                                leafs_to_rules_count_map=self.placement['maps']['leafs_to_rules_count'],
                                max_rules_perf_leaf=self.network['num_rules_per_leaf'],
                                num_hosts_per_leaf=self.network['num_hosts_per_leaf'])
