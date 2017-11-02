import pandas as pd
import numpy as np
from simulation.utils import bar_range


class Data:
    def __init__(self, cloud):
        self.network = cloud.data['network']
        self.tenants = cloud.data['tenants']
        self.tenants_maps = self.tenants['maps']
        self.placement = cloud.data['placement']

    def vm_count_for_all_tenants(self):
        return pd.Series([self.tenants_maps[t]['vm_count'] for t in range(self.tenants['num_tenants'])])

    def group_count_for_all_tenants(self):
        return pd.Series([self.tenants_maps[t]['group_count'] for t in range(self.tenants['num_tenants'])])

    def group_sizes_for_all_tenants(self):
        _group_sizes_for_all_tenants = []
        for t in range(self.tenants['num_tenants']):
            for g in range(self.tenants_maps[t]['group_count']):
                _group_sizes_for_all_tenants += [self.tenants_maps[t]['groups_map'][g]['size']]

        return pd.Series(_group_sizes_for_all_tenants)

    def leafs_for_all_groups_in_all_tenants(self):
        _leafs_for_all_groups_in_all_tenants = []
        for t in range(self.tenants['num_tenants']):
            for g in range(self.tenants_maps[t]['group_count']):
                _leafs_for_all_groups_in_all_tenants += [self.tenants_maps[t]['groups_map'][g]['leaf_count']]

        return pd.Series(_leafs_for_all_groups_in_all_tenants)

    def percentage_of_groups_covered_with_varying_bitmaps(self, num_bitmaps):
        categories = pd.cut(self.leafs_for_all_groups_in_all_tenants(), [i for i in range(-1, num_bitmaps + 1)],
                            right=True, labels=[i for i in range(0, num_bitmaps + 1)]).value_counts()
        percentage_categories = np.cumsum(categories.sort_index()).astype(np.double) / self.tenants['group_count'] * 100
        return percentage_categories

    def rules_for_all_leafs(self):
        return pd.Series(self.placement['maps']['leafs_to_rules_count'])

    def redundancy_for_all_groups_in_all_tenants(self):
        _redundancy_for_all_groups_in_all_tenants = []
        for t in range(self.tenants['num_tenants']):
            for g in range(self.tenants_maps[t]['group_count']):
                if self.tenants_maps[t]['groups_map'][g]['leaf_count'] > self.placement['num_bitmaps']:
                    _redundancy_for_all_groups_in_all_tenants += \
                        [self.tenants_maps[t]['groups_map'][g]['r'] /
                         (self.tenants_maps[t]['groups_map'][g]['r'] + self.tenants_maps[t]['groups_map'][g]['size'])
                         * 100]

        return pd.Series(_redundancy_for_all_groups_in_all_tenants)

    def traffic_stats(self):
        _actual_traffic_for_all_leafs = dict()
        _redundant_traffic_for_all_leafs = dict()
        for t in bar_range(self.tenants['num_tenants'], desc='stats'):
            for g in range(self.tenants_maps[t]['group_count']):
                for l in self.tenants_maps[t]['groups_map'][g]['leafs']:
                    if not (l in _actual_traffic_for_all_leafs):
                        _actual_traffic_for_all_leafs[l] = [0] * self.network['num_hosts_per_leaf']
                    for i, b in enumerate(self.tenants_maps[t]['groups_map'][g]['leafs_map'][l]['bitmap']):
                        if b:
                            _actual_traffic_for_all_leafs[l][i] += 1

                    if '~bitmap' in self.tenants_maps[t]['groups_map'][g]['leafs_map'][l]:
                        if not (l in _redundant_traffic_for_all_leafs):
                            _redundant_traffic_for_all_leafs[l] = [0] * self.network['num_hosts_per_leaf']
                        for i, b in enumerate(self.tenants_maps[t]['groups_map'][g]['leafs_map'][l]['~bitmap']):
                            if b:
                                _redundant_traffic_for_all_leafs[l][i] += 1

        return _actual_traffic_for_all_leafs, _redundant_traffic_for_all_leafs

    @staticmethod
    def traffic_overhead(actual_traffic, redundant_traffic):
        _actual_traffic = 0
        for l in actual_traffic:
            _actual_traffic += sum(actual_traffic[l])

        _redundant_traffic = 0
        for l in redundant_traffic:
            _redundant_traffic += sum(redundant_traffic[l])

        return _redundant_traffic / (_actual_traffic + _redundant_traffic) * 100

    @staticmethod
    def actual_traffic_rate(actual_traffic):
        _actual_traffic_rate = []
        for l in actual_traffic:
            _actual_traffic_rate += actual_traffic[l]

        return pd.Series(_actual_traffic_rate)

    @staticmethod
    def redundant_traffic_rate(redundant_traffic):
        _redundant_traffic_rate = []
        for l in redundant_traffic:
            _redundant_traffic_rate += redundant_traffic[l]

        return pd.Series(_redundant_traffic_rate)

    def total_traffic_rate(self, actual_traffic, redundant_traffic):
        _total_traffic = dict()
        for l in actual_traffic:
            if l in redundant_traffic:
                _total_traffic[l] = [0] * self.network['num_hosts_per_leaf']
                for i in range(self.network['num_hosts_per_leaf']):
                    _total_traffic[l][i] = actual_traffic[l][i] + redundant_traffic[l][i]
            else:
                _total_traffic[l] = actual_traffic[l]

        _total_traffic_rate = []
        for l in _total_traffic:
            _total_traffic_rate += _total_traffic[l]

        return pd.Series(_total_traffic_rate)
