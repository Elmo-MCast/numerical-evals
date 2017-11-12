import pandas as pd
from simulation.utils import bar_range, popcount


class Data:
    def __init__(self, data, num_tenants=3000, num_leafs=576, num_hosts_per_leaf=48, num_bitmaps=10,
                 log_dir=None):
        self.num_tenants = num_tenants
        self.num_leafs = num_leafs
        self.num_hosts_per_leaf = num_hosts_per_leaf
        self.num_bitmaps = num_bitmaps
        self.log_dir = log_dir

        self.tenants = data['tenants']
        self.tenants_maps = self.tenants['maps']

        self.optimizer = data['optimizer']

    def algorithm_elapse_time(self):
        _algorithm_elapse_time = pd.Series(self.optimizer['algorithm_elapse_time'])

        if self.log_dir is not None:
            _algorithm_elapse_time.to_csv(self.log_dir + "/algorithm_elapse_time.csv")

        return _algorithm_elapse_time

    def vm_count_per_tenant(self):
        _vm_count_per_tenant = pd.Series([self.tenants_maps[t]['vm_count'] for t in range(self.num_tenants)])

        if self.log_dir is not None:
            _vm_count_per_tenant.to_csv(self.log_dir + "/vm_count_per_tenant.csv")

        return _vm_count_per_tenant

    def group_count_per_tenant(self):
        _group_count_per_tenant = pd.Series([self.tenants_maps[t]['group_count'] for t in range(self.num_tenants)])

        if self.log_dir is not None:
            _group_count_per_tenant.to_csv(self.log_dir + "/group_count_per_tenant.csv")

        return _group_count_per_tenant

    def group_size_per_group_per_tenant(self):
        _group_size_per_group_per_tenant = []

        for t in range(self.num_tenants):
            tenant_maps = self.tenants_maps[t]
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']

            for g in range(group_count):
                _group_size_per_group_per_tenant += [groups_map[g]['size']]

        _group_size_per_group_per_tenant = pd.Series(_group_size_per_group_per_tenant)

        if self.log_dir is not None:
            _group_size_per_group_per_tenant.to_csv(self.log_dir + "/group_size_per_group_per_tenant.csv")

        return _group_size_per_group_per_tenant

    def leaf_count_per_group_per_tenant(self):
        _leaf_count_per_group_per_tenant = []

        for t in range(self.num_tenants):
            tenant_maps = self.tenants_maps[t]
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']

            for g in range(group_count):
                _leaf_count_per_group_per_tenant += [groups_map[g]['leaf_count']]

        _leaf_count_per_group_per_tenant = pd.Series(_leaf_count_per_group_per_tenant)

        if self.log_dir is not None:
            _leaf_count_per_group_per_tenant.to_csv(self.log_dir + "/leaf_count_per_group_per_tenant.csv")

        return _leaf_count_per_group_per_tenant

    # def percentage_of_groups_covered_with_varying_bitmaps(self, num_bitmaps):
    #     categories = pd.cut(self.leafs_for_all_groups_for_all_tenants(), [i for i in range(-1, num_bitmaps + 1)],
    #                         right=True, labels=[i for i in range(0, num_bitmaps + 1)]).value_counts()
    #     percentage_categories = pd.Series(np.cumsum(categories.sort_index()).astype(np.double) /
    #                                       self.tenants['group_count'] * 100)
    #     if self.log_dir is not None:
    #         percentage_categories.to_csv(self.log_dir + "/percentage_of_groups_covered_with_varying_bitmaps.csv")
    #     return percentage_categories

    def rule_count_per_leaf(self):
        _rule_count_per_leaf = pd.Series(self.optimizer['leafs_to_rules_count'])

        if self.log_dir is not None:
            _rule_count_per_leaf.to_csv(self.log_dir + "/rule_count_per_leaf.csv")

        return _rule_count_per_leaf

    def traffic_overhead_per_group_per_tenant(self):
        _traffic_overhead_per_group_per_tenant = []

        for t in bar_range(self.num_tenants, desc='progress'):
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

                _traffic_overhead_per_group_per_tenant += [_redundant_traffic / _actual_traffic]

        _traffic_overhead_per_group_per_tenant = pd.Series(_traffic_overhead_per_group_per_tenant)

        if self.log_dir is not None:
            _traffic_overhead_per_group_per_tenant.to_csv(
                self.log_dir + "/traffic_overhead_per_group_per_tenant.csv")

        return _traffic_overhead_per_group_per_tenant

    def traffic_stats(self):
        _actual_traffic_per_leaf = dict()
        _unwanted_traffic_per_leaf = dict()

        for l in range(self.num_leafs):
            _actual_traffic_per_leaf[l] = [0] * self.num_hosts_per_leaf
            _unwanted_traffic_per_leaf[l] = [0] * self.num_hosts_per_leaf

        for t in bar_range(self.num_tenants, desc='progress'):
            tenant_maps = self.tenants_maps[t]
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']

            for g in range(group_count):
                group_map = groups_map[g]
                leafs_map = group_map['leafs_map']

                for l in leafs_map:
                    leaf_map = leafs_map[l]
                    for i, b in enumerate(bin(leaf_map['bitmap'])[:1:-1]):
                        if b == '1':
                            _actual_traffic_per_leaf[l][i] += 1

                    if '~bitmap' in leaf_map:
                        for i, b in enumerate(bin(leaf_map['~bitmap'])[:1:-1]):
                            if b == '1':
                                _unwanted_traffic_per_leaf[l][i] += 1

        return _actual_traffic_per_leaf, _unwanted_traffic_per_leaf

    def traffic_overhead(self, actual_traffic_per_leaf, unwanted_traffic_per_leaf):
        _actual_traffic_per_leaf = 0
        for l in actual_traffic_per_leaf:
            _actual_traffic_per_leaf += sum(actual_traffic_per_leaf[l])

        _unwanted_traffic_per_leaf = 0
        for l in unwanted_traffic_per_leaf:
            _unwanted_traffic_per_leaf += sum(unwanted_traffic_per_leaf[l])

        _traffic_overhead = pd.Series((_unwanted_traffic_per_leaf / _actual_traffic_per_leaf))

        if self.log_dir is not None:
            _traffic_overhead.to_csv(self.log_dir + "/traffic_overhead.csv")

        return _traffic_overhead

    def actual_traffic_per_link(self, traffic_per_leaf):
        _traffic_per_link = []
        for l in traffic_per_leaf:
            _traffic_per_link += traffic_per_leaf[l]
        _traffic_per_link = pd.Series(_traffic_per_link)

        if self.log_dir is not None:
            _traffic_per_link.to_csv(self.log_dir + "/actual_traffic_per_link.csv")

        return _traffic_per_link

    def unwanted_traffic_per_link(self, traffic_per_leaf):
        _traffic_per_link = []
        for l in traffic_per_leaf:
            _traffic_per_link += traffic_per_leaf[l]
        _traffic_per_link = pd.Series(_traffic_per_link)

        if self.log_dir is not None:
            _traffic_per_link.to_csv(self.log_dir + "/unwanted_traffic_per_link.csv")

        return _traffic_per_link

    def total_traffic_per_link(self, actual_traffic_per_leaf, unwanted_traffic_per_leaf):
        _total_traffic_per_leaf = dict()
        for l in actual_traffic_per_leaf:
            if l in unwanted_traffic_per_leaf:
                _total_traffic_per_leaf[l] = [0] * self.num_hosts_per_leaf
                for i in range(self.num_hosts_per_leaf):
                    _total_traffic_per_leaf[l][i] = actual_traffic_per_leaf[l][i] + \
                                                         unwanted_traffic_per_leaf[l][i]
            else:
                _total_traffic_per_leaf[l] = actual_traffic_per_leaf[l]

        _total_traffic_per_link = []
        for l in _total_traffic_per_leaf:
            _total_traffic_per_link += _total_traffic_per_leaf[l]
        _total_traffic_per_link = pd.Series(_total_traffic_per_link)

        if self.log_dir is not None:
            _total_traffic_per_link.to_csv(self.log_dir + "/total_traffic_per_link.csv")

        return _total_traffic_per_link

    def traffic_overhead_per_link(self, total_traffic_per_link, actual_traffic_per_link):
        link_count = len(total_traffic_per_link)
        _traffic_overhead_per_link = [0] * link_count
        for i in bar_range(link_count, desc='progress'):
            if total_traffic_per_link[i] != 0:
                _traffic_overhead_per_link[i] = ((total_traffic_per_link[i] - actual_traffic_per_link[i]) /
                                                 actual_traffic_per_link[i])
        _traffic_overhead_per_link = pd.Series(_traffic_overhead_per_link)

        if self.log_dir is not None:
            _traffic_overhead_per_link.to_csv(self.log_dir + "/traffic_overhead_per_link.csv")
        return _traffic_overhead_per_link

    def log(self):
        self.algorithm_elapse_time()
        self.vm_count_per_tenant()
        self.group_count_per_tenant()
        self.group_size_per_group_per_tenant()
        self.leaf_count_per_group_per_tenant()
        # self.percentage_of_groups_covered_with_varying_bitmaps(self.num_bitmaps)
        self.rule_count_per_leaf()
        self.traffic_overhead_per_group_per_tenant()
        at_dict, ut_dict = self.traffic_stats()
        self.traffic_overhead(at_dict, ut_dict)
        at_list = self.actual_traffic_per_link(at_dict)
        ut_list = self.unwanted_traffic_per_link(ut_dict)
        tt_list = self.total_traffic_per_link(at_dict, ut_dict)
        self.traffic_overhead_per_link(tt_list, at_list)
