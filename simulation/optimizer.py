from timeit import default_timer as timer
import numpy as np
from simulation.algorithms import algorithms
from simulation.utils import bar_range


class Optimizer:
    def __init__(self, data, max_batch_size=1, algorithm='single_match', num_leafs_per_bitmap=3,
                 redundancy_per_bitmap=20):
        self.data = data
        self.max_batch_size = max_batch_size
        self.algorithm = algorithm
        self.num_leafs_per_bitmap = num_leafs_per_bitmap
        self.redundancy_per_bitmap = redundancy_per_bitmap
        self.algorithm_elapse_time = []

        self.network = self.data['network']
        self.network_maps = self.network['maps']

        self.num_leafs = self.network['num_leafs']
        self.num_rules_per_leaf = self.network['num_rules_per_leaf']

        self.tenants = self.data['tenants']
        self.tenants_maps = self.tenants['maps']

        self.num_tenants = self.tenants['num_tenants']

        self.placement = self.data['placement']
        self.placement['maps'] = {'leafs_to_rules_count': {l: 0 for l in range(self.num_leafs)}}

        self.num_bitmaps = self.placement['num_bitmaps']
        self.leafs_to_rules_count_map = self.placement['maps']['leafs_to_rules_count']

        self.data['optimizer'] = {'max_batch_size': max_batch_size,
                                  'algorithm': algorithm,
                                  'max_leafs_per_bitmap': num_leafs_per_bitmap,
                                  'redundancy_per_bitmap': redundancy_per_bitmap,
                                  'algorithm_elapse_time': self.algorithm_elapse_time}

        self._optimize()

    def _optimize(self):
        if self.max_batch_size <= 1:
            for t in bar_range(self.num_tenants, desc='optimizer'):
                group_count = self.tenants_maps[t]['group_count']
                groups_map = self.tenants_maps[t]['groups_map']
                for g in range(group_count):
                    start = timer()
                    algorithms.run(
                        algorithm=self.algorithm,
                        data=groups_map[g],
                        max_bitmaps=self.num_bitmaps,
                        max_leafs_per_bitmap=self.num_leafs_per_bitmap,
                        redundancy_per_bitmap=self.redundancy_per_bitmap,
                        leafs_to_rules_count_map=self.leafs_to_rules_count_map,
                        max_rules_per_leaf=self.num_rules_per_leaf)
                    end = timer()
                    self.algorithm_elapse_time += [end - start]
        else:
            batch_size = np.random.randint(low=1, high=self.max_batch_size + 1, size=1)[0]
            running_batch_size = 0
            running_batch_list = []

            for t in bar_range(self.num_tenants, desc='optimizer'):
                group_count = self.tenants_maps[t]['group_count']
                groups_map = self.tenants_maps[t]['groups_map']
                for g in range(group_count):
                    running_batch_list += [groups_map[g]]
                    running_batch_size += 1

                    if running_batch_size == batch_size:
                        running_batch_list = sorted(running_batch_list, key=lambda item: item['leaf_count'])

                        for _g in running_batch_list:
                            algorithms.run(
                                algorithm=self.algorithm,
                                data=_g,
                                max_bitmaps=self.num_bitmaps,
                                max_leafs_per_bitmap=self.num_leafs_per_bitmap,
                                redundancy_per_bitmap=self.redundancy_per_bitmap,
                                leafs_to_rules_count_map=self.leafs_to_rules_count_map,
                                max_rules_per_leaf=self.num_rules_per_leaf)

                        batch_size = np.random.randint(low=1, high=self.max_batch_size + 1, size=1)[0]
                        running_batch_size = 0
                        running_batch_list = []

                if (t + 1) == self.num_tenants:
                    running_batch_list = sorted(running_batch_list, key=lambda item: item['leaf_count'])

                    for _g in running_batch_list:
                        algorithms.run(
                            algorithm=self.algorithm,
                            data=_g,
                            max_bitmaps=self.num_bitmaps,
                            max_leafs_per_bitmap=self.num_leafs_per_bitmap,
                            redundancy_per_bitmap=self.redundancy_per_bitmap,
                            leafs_to_rules_count_map=self.leafs_to_rules_count_map,
                            max_rules_per_leaf=self.num_rules_per_leaf)
