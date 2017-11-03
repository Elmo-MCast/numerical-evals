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
        for t in bar_range(self.tenants['num_tenants'], desc='progress'):
            for g in range(self.tenants_maps[t]['group_count']):
                _actual_traffic = 0
                _redundant_traffic = 0
                for l in self.tenants_maps[t]['groups_map'][g]['leafs']:
                    _actual_traffic += np.count_nonzero(self.tenants_maps[t]['groups_map'][g]['leafs_map'][l]['bitmap'])

                    if '~bitmap' in self.tenants_maps[t]['groups_map'][g]['leafs_map'][l]:
                        _redundant_traffic += \
                            np.count_nonzero(self.tenants_maps[t]['groups_map'][g]['leafs_map'][l]['~bitmap'])

                _redundancy_for_all_groups_in_all_tenants += \
                    [_redundant_traffic / (_actual_traffic + _redundant_traffic) * 100]

        return pd.Series(_redundancy_for_all_groups_in_all_tenants)

    def traffic_stats(self):
        _actual_traffic_for_all_leafs = dict()
        _unwanted_traffic_for_all_leafs = dict()
        for t in bar_range(self.tenants['num_tenants'], desc='progress'):
            for g in range(self.tenants_maps[t]['group_count']):
                for l in self.tenants_maps[t]['groups_map'][g]['leafs']:
                    if not (l in _actual_traffic_for_all_leafs):
                        _actual_traffic_for_all_leafs[l] = [0] * self.network['num_hosts_per_leaf']
                    for i, b in enumerate(self.tenants_maps[t]['groups_map'][g]['leafs_map'][l]['bitmap']):
                        if b:
                            _actual_traffic_for_all_leafs[l][i] += 1

                    if '~bitmap' in self.tenants_maps[t]['groups_map'][g]['leafs_map'][l]:
                        if not (l in _unwanted_traffic_for_all_leafs):
                            _unwanted_traffic_for_all_leafs[l] = [0] * self.network['num_hosts_per_leaf']
                        for i, b in enumerate(self.tenants_maps[t]['groups_map'][g]['leafs_map'][l]['~bitmap']):
                            if b:
                                _unwanted_traffic_for_all_leafs[l][i] += 1

        return _actual_traffic_for_all_leafs, _unwanted_traffic_for_all_leafs

    @staticmethod
    def traffic_overhead(actual_traffic_for_all_leafs, unwanted_traffic_for_all_leafs):
        _actual_traffic_for_all_leafs = 0
        for l in actual_traffic_for_all_leafs:
            _actual_traffic_for_all_leafs += sum(actual_traffic_for_all_leafs[l])

        _unwanted_traffic_for_all_leafs = 0
        for l in unwanted_traffic_for_all_leafs:
            _unwanted_traffic_for_all_leafs += sum(unwanted_traffic_for_all_leafs[l])

        return _unwanted_traffic_for_all_leafs / (_actual_traffic_for_all_leafs + _unwanted_traffic_for_all_leafs) * 100

    @staticmethod
    def actual_traffic_per_link(traffic_for_all_leafs):
        _traffic_per_link = []
        for l in traffic_for_all_leafs:
            _traffic_per_link += traffic_for_all_leafs[l]

        return pd.Series(_traffic_per_link)

    @staticmethod
    def unwanted_traffic_per_link(traffic_for_all_leafs):
        _traffic_per_link = []
        for l in traffic_for_all_leafs:
            _traffic_per_link += traffic_for_all_leafs[l]

        return pd.Series(_traffic_per_link)

    def total_traffic_per_link(self, actual_traffic_for_all_leafs, unwanted_traffic_for_all_leafs):
        _total_traffic_for_all_leafs = dict()
        for l in actual_traffic_for_all_leafs:
            if l in unwanted_traffic_for_all_leafs:
                _total_traffic_for_all_leafs[l] = [0] * self.network['num_hosts_per_leaf']
                for i in range(self.network['num_hosts_per_leaf']):
                    _total_traffic_for_all_leafs[l][i] = actual_traffic_for_all_leafs[l][i] + unwanted_traffic_for_all_leafs[l][i]
            else:
                _total_traffic_for_all_leafs[l] = actual_traffic_for_all_leafs[l]

        _total_traffic_per_link = []
        for l in _total_traffic_for_all_leafs:
            _total_traffic_per_link += _total_traffic_for_all_leafs[l]

        return pd.Series(_total_traffic_per_link)

    @staticmethod
    def traffic_overhead_per_link(total_traffic_per_link, actual_traffic_per_link):
        _traffic_overhead_per_link = []

        for i in bar_range(len(total_traffic_per_link), desc='progress'):
            _traffic_overhead_per_link += [(total_traffic_per_link[i] - actual_traffic_per_link[i]) /
                                           total_traffic_per_link[i] * 100]

        return pd.Series(_traffic_overhead_per_link)
