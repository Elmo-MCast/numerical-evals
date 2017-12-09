from timeit import default_timer as timer
import numpy as np
from simulation.algorithms import algorithms
from simulation.utils import bar_range


class Optimizer:
    def __init__(self, data, algorithm='single-match', num_bitmaps=10, num_nodes_per_bitmap=3, redundancy_per_bitmap=20,
                 num_rules=64000, num_nodes=528, num_tenants=3000, probability=1.0 * 2 / 3, node_type='leafs'):
        self.data = data
        self.algorithm = algorithm
        self.num_bitmaps = num_bitmaps
        self.num_leafs_per_bitmap = num_nodes_per_bitmap
        self.redundancy_per_bitmap = redundancy_per_bitmap
        self.num_rules = num_rules
        self.num_nodes = num_nodes
        self.num_tenants = num_tenants
        self.probability = probability
        self.node_type = node_type

        self.algorithm_elapse_time = []
        self.rules_count_map = [0] * self.num_nodes

        self.tenants = self.data['tenants']
        self.tenants_maps = self.tenants['maps']

        self.data['optimizer'] = {
            self.node_type: {
                'algorithm_elapse_time': self.algorithm_elapse_time,
                'rules_count': self.rules_count_map}
        }

        self._run()

    def _run(self):
        for t in bar_range(self.num_tenants, desc='optimizer:%s' % self.algorithm):
            tenant_maps = self.tenants_maps[t]
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']
            for g in range(group_count):
                group_map = groups_map[g]
                nodes_map = group_map['leafs_map'] if self.node_type == 'leafs' else group_map['pods_map']

                start = timer()
                default_bitmap = algorithms.run(
                    algorithm=self.algorithm,
                    nodes_map=nodes_map,
                    max_bitmaps=self.num_bitmaps,
                    max_nodes_per_bitmap=self.num_leafs_per_bitmap,
                    redundancy_per_bitmap=self.redundancy_per_bitmap,
                    rules_count_map=self.rules_count_map,
                    max_rules=self.num_rules,
                    probability=self.probability)
                if default_bitmap:
                    group_map['%s_default_bitmap' % self.node_type] = default_bitmap
                end = timer()
                self.algorithm_elapse_time += [end - start]
