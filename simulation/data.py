import pandas as pd
import numpy as np
from simulation.utils import bar_range, popcount


class Data:
    def __init__(self, data, num_tenants=3000, num_hosts_per_leaf=48, log_dir=None):
        self.num_tenants = num_tenants
        self.num_hosts_per_leaf = num_hosts_per_leaf
        self.log_dir = log_dir

        self.tenants = data['tenants']
        self.tenants_maps = self.tenants['maps']

        self.optimizer = data['optimizer']

    def algorithm_elapse_time(self):
        _algorithm_elapse_time = pd.Series(self.optimizer['algorithm_elapse_time'])
        if self.log_dir is not None:
            _algorithm_elapse_time.to_csv(self.log_dir + "/algorithm_elapse_time.csv")
        return _algorithm_elapse_time

    def vm_count_for_all_tenants(self):
        _vm_count_for_all_tenants = pd.Series([self.tenants_maps[t]['vm_count'] for t in range(self.num_tenants)])
        if self.log_dir is not None:
            _vm_count_for_all_tenants.to_csv(self.log_dir + "/vm_count_for_all_tenants.csv")
        return _vm_count_for_all_tenants

    def group_count_for_all_tenants(self):
        _group_count_for_all_tenants = pd.Series([self.tenants_maps[t]['group_count'] for t in range(self.num_tenants)])
        if self.log_dir is not None:
            _group_count_for_all_tenants.to_csv(self.log_dir + "/group_count_for_all_tenants.csv")
        return _group_count_for_all_tenants

    def group_sizes_for_all_tenants(self):
        _group_sizes_for_all_tenants = []
        for t in range(self.num_tenants):
            tenant_maps = self.tenants_maps[t]
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']
            for g in range(group_count):
                _group_sizes_for_all_tenants += [groups_map[g]['size']]
        _group_sizes_for_all_tenants = pd.Series(_group_sizes_for_all_tenants)
        if self.log_dir is not None:
            _group_sizes_for_all_tenants.to_csv(self.log_dir + "/group_sizes_for_all_tenants.csv")
        return _group_sizes_for_all_tenants

    def leafs_for_all_groups_in_all_tenants(self):
        _leafs_for_all_groups_in_all_tenants = []
        for t in range(self.num_tenants):
            tenant_maps = self.tenants_maps[t]
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']
            for g in range(group_count):
                _leafs_for_all_groups_in_all_tenants += [groups_map[g]['leaf_count']]
        _leafs_for_all_groups_in_all_tenants = pd.Series(_leafs_for_all_groups_in_all_tenants)
        if self.log_dir is not None:
            _leafs_for_all_groups_in_all_tenants.to_csv(self.log_dir + "/leafs_for_all_groups_in_all_tenants.csv")
        return _leafs_for_all_groups_in_all_tenants

    def percentage_of_groups_covered_with_varying_bitmaps(self, num_bitmaps):
        categories = pd.cut(self.leafs_for_all_groups_in_all_tenants(), [i for i in range(-1, num_bitmaps + 1)],
                            right=True, labels=[i for i in range(0, num_bitmaps + 1)]).value_counts()
        percentage_categories = pd.Series(np.cumsum(categories.sort_index()).astype(np.double) /
                                          self.tenants['group_count'] * 100)
        if self.log_dir is not None:
            percentage_categories.to_csv(self.log_dir + "/percentage_categories.csv")
        return percentage_categories

    def rules_for_all_leafs(self):
        _rules_for_all_leafs = pd.Series(self.optimizer['leafs_to_rules_count'])
        if self.log_dir is not None:
            _rules_for_all_leafs.to_csv(self.log_dir + "/rules_for_all_leafs.csv")
        return _rules_for_all_leafs

    def redundancy_for_all_groups_in_all_tenants(self):
        _redundancy_for_all_groups_in_all_tenants = []
        for t in bar_range(self.tenants['num_tenants'], desc='progress'):
            tenant_maps = self.tenants_maps[t]
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']
            for g in range(group_count):
                group_map = groups_map[g]
                leafs_map = group_map['leafs_map']
                _actual_traffic = 0
                _redundant_traffic = 0
                for l in leafs_map:
                    leaf_map = leafs_map[l]
                    _actual_traffic += popcount(leaf_map['bitmap'])

                    if '~bitmap' in leaf_map:
                        _redundant_traffic += popcount(leaf_map['~bitmap'])
                _redundancy_for_all_groups_in_all_tenants += \
                    [_redundant_traffic / (_actual_traffic + _redundant_traffic) * 100]

        _redundancy_for_all_groups_in_all_tenants = pd.Series(_redundancy_for_all_groups_in_all_tenants)
        if self.log_dir is not None:
            _redundancy_for_all_groups_in_all_tenants.to_csv(self.log_dir +
                                                             "/redundancy_for_all_groups_in_all_tenants.csv")
        return _redundancy_for_all_groups_in_all_tenants

    def traffic_stats(self):
        _actual_traffic_for_all_leafs = pd.DataFrame()
        _unwanted_traffic_for_all_leafs = pd.DataFrame()
        for t in bar_range(self.num_tenants, desc='progress'):
            tenant_maps = self.tenants_maps[t]
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']
            for g in range(group_count):
                group_map = groups_map[g]
                leafs_map = group_map['leafs_map']
                for l in leafs_map:
                    leaf_map = leafs_map[l]
                    if not (l in _actual_traffic_for_all_leafs):
                        _actual_traffic_for_all_leafs[l] = [0] * self.num_hosts_per_leaf
                    for i, b in enumerate(bin(leaf_map['bitmap'])[:1:-1]):
                        if b == '1':
                            _actual_traffic_for_all_leafs[l][i] += 1

                    if '~bitmap' in leaf_map:
                        if not (l in _unwanted_traffic_for_all_leafs):
                            _unwanted_traffic_for_all_leafs[l] = [0] * self.num_hosts_per_leaf
                        for i, b in enumerate(bin(leaf_map['~bitmap'])[:1:-1]):
                            if b == '1':
                                _unwanted_traffic_for_all_leafs[l][i] += 1

        if self.log_dir is not None:
            _actual_traffic_for_all_leafs.to_csv(self.log_dir + "/actual_traffic_for_all_leafs.csv")
            _unwanted_traffic_for_all_leafs.to_csv(self.log_dir + "/unwanted_traffic_for_all_leafs.csv")
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
                _total_traffic_for_all_leafs[l] = [0] * self.num_hosts_per_leaf
                for i in range(self.num_hosts_per_leaf):
                    _total_traffic_for_all_leafs[l][i] = actual_traffic_for_all_leafs[l][i] + \
                                                         unwanted_traffic_for_all_leafs[l][i]
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
