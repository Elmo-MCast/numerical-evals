from timeit import default_timer as timer
import numpy as np
from simulation.algorithms import algorithms
from simulation.utils import bar_range


class Optimizer:
    def __init__(self, data,
                 max_batch_size=1, algorithm='single-match',
                 num_leafs_per_bitmap=3, redundancy_per_bitmap=20, num_rules_per_leaf=6400,
                 num_leafs=576, num_bitmaps=10, num_tenants=3000, probability=1.0 * 2 / 3):
        self.data = data
        self.max_batch_size = max_batch_size
        self.algorithm = algorithm
        self.num_leafs_per_bitmap = num_leafs_per_bitmap
        self.redundancy_per_bitmap = redundancy_per_bitmap
        self.num_rules_per_leaf = num_rules_per_leaf
        self.num_leafs = num_leafs
        self.num_tenants = num_tenants
        self.algorithm_elapse_time = []
        self.leafs_to_rules_count_map = [0] * self.num_leafs
        self.num_bitmaps = num_bitmaps
        self.probability = probability

        self.tenants = self.data['tenants']
        self.tenants_maps = self.tenants['maps']

        self.data['optimizer'] = {'algorithm_elapse_time': self.algorithm_elapse_time,
                                  'leafs_to_rules_count': self.leafs_to_rules_count_map}

        self._run()

    def _run(self):
        if self.max_batch_size <= 1:
            for t in bar_range(self.num_tenants, desc='optimizer:%s' % self.algorithm):
                tenant_maps = self.tenants_maps[t]
                group_count = tenant_maps['group_count']
                groups_map = tenant_maps['groups_map']
                for g in range(group_count):
                    start = timer()
                    algorithms.run(
                        algorithm=self.algorithm,
                        group=groups_map[g],
                        max_bitmaps=self.num_bitmaps,
                        max_leafs_per_bitmap=self.num_leafs_per_bitmap,
                        redundancy_per_bitmap=self.redundancy_per_bitmap,
                        leafs_to_rules_count_map=self.leafs_to_rules_count_map,
                        max_rules_per_leaf=self.num_rules_per_leaf,
                        probability=self.probability)
                    end = timer()
                    self.algorithm_elapse_time += [end - start]
        else:
            batch_size = np.random.randint(low=1, high=self.max_batch_size + 1, size=1)[0]
            running_batch_size = 0
            running_batch_list = []

            for t in bar_range(self.num_tenants, desc='optimizer:%s' % self.algorithm):
                tenant_maps = self.tenants_maps[t]
                group_count = tenant_maps['group_count']
                groups_map = tenant_maps['groups_map']
                for g in range(group_count):
                    running_batch_list += [groups_map[g]]
                    running_batch_size += 1

                    if running_batch_size == batch_size:
                        running_batch_list = sorted(running_batch_list, key=lambda item: len(item['leafs_map']))

                        for _g in running_batch_list:
                            algorithms.run(
                                algorithm=self.algorithm,
                                group=_g,
                                max_bitmaps=self.num_bitmaps,
                                max_leafs_per_bitmap=self.num_leafs_per_bitmap,
                                redundancy_per_bitmap=self.redundancy_per_bitmap,
                                leafs_to_rules_count_map=self.leafs_to_rules_count_map,
                                max_rules_per_leaf=self.num_rules_per_leaf,
                                probability=self.probability)

                        batch_size = np.random.randint(low=1, high=self.max_batch_size + 1, size=1)[0]
                        running_batch_size = 0
                        running_batch_list = []

                if (t + 1) == self.num_tenants:
                    running_batch_list = sorted(running_batch_list, key=lambda item: len(item['leafs_map']))

                    for _g in running_batch_list:
                        algorithms.run(
                            algorithm=self.algorithm,
                            group=_g,
                            max_bitmaps=self.num_bitmaps,
                            max_leafs_per_bitmap=self.num_leafs_per_bitmap,
                            redundancy_per_bitmap=self.redundancy_per_bitmap,
                            leafs_to_rules_count_map=self.leafs_to_rules_count_map,
                            max_rules_per_leaf=self.num_rules_per_leaf,
                            probability=self.probability)
