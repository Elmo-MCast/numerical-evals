import pandas as pd
from functools import reduce
from simulation.utils import bar_range, popcount


class Data:
    def __init__(self, data, num_tenants=3000, num_pods=11, num_leafs_per_pod=48, num_hosts_per_leaf=48, num_bitmaps=10,
                 log_dir=None, node_type='leafs'):
        self.num_tenants = num_tenants
        self.num_pods = num_pods
        self.num_leafs_per_pod = num_leafs_per_pod
        self.num_hosts_per_leaf = num_hosts_per_leaf
        self.num_bitmaps = num_bitmaps
        self.log_dir = log_dir
        self.node_type = node_type

        self.tenants = data['tenants']
        self.tenants_maps = self.tenants['maps']

        self.optimizer = data['optimizer'][self.node_type]

    def vm_count_per_tenant(self):
        _vm_count_per_tenant = pd.Series([self.tenants_maps[t]['vm_count'] for t in range(self.num_tenants)])

        if self.log_dir is not None:
            _vm_count_per_tenant.to_csv(self.log_dir + "/vm_count_per_tenant.csv", index=False)

        return _vm_count_per_tenant

    def group_count_per_tenant(self):
        _group_count_per_tenant = pd.Series([self.tenants_maps[t]['group_count'] for t in range(self.num_tenants)])

        if self.log_dir is not None:
            _group_count_per_tenant.to_csv(self.log_dir + "/group_count_per_tenant.csv", index=False)

        return _group_count_per_tenant

    def group_size_per_group_per_tenant(self):
        _group_size_per_group_per_tenant = []

        for t in bar_range(self.num_tenants, "data:group_size_per_group_per_tenant:"):
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

        for t in bar_range(self.num_tenants, "data:leaf_count_per_group_per_tenant:"):
            tenant_maps = self.tenants_maps[t]
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']

            for g in range(group_count):
                _leaf_count_per_group_per_tenant += [len(groups_map[g]['leafs_map'])]

        _leaf_count_per_group_per_tenant = pd.Series(_leaf_count_per_group_per_tenant)

        if self.log_dir is not None:
            _leaf_count_per_group_per_tenant.to_csv(self.log_dir + "/leaf_count_per_group_per_tenant.csv", index=False)

        return _leaf_count_per_group_per_tenant

    def pod_count_per_group_per_tenant(self):
        _pod_count_per_group_per_tenant = []

        for t in bar_range(self.num_tenants, "data:pod_count_per_group_per_tenant:"):
            tenant_maps = self.tenants_maps[t]
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']

            for g in range(group_count):
                _pod_count_per_group_per_tenant += [len(groups_map[g]['pods_map'])]

        _pod_count_per_group_per_tenant = pd.Series(_pod_count_per_group_per_tenant)

        if self.log_dir is not None:
            _pod_count_per_group_per_tenant.to_csv(self.log_dir + "/pod_count_per_group_per_tenant.csv", index=False)

        return _pod_count_per_group_per_tenant

    def algorithm_elapse_time(self):
        _algorithm_elapse_time = pd.Series(self.optimizer['algorithm_elapse_time'])

        if self.log_dir is not None:
            _algorithm_elapse_time.to_csv(self.log_dir + "/%s_algorithm_elapse_time.csv" % self.node_type, index=False)

        return _algorithm_elapse_time


    # def percentage_of_groups_covered_with_varying_bitmaps(self, num_bitmaps):
    #     categories = pd.cut(self.leafs_for_all_groups_for_all_tenants(), [i for i in range(-1, num_bitmaps + 1)],
    #                         right=True, labels=[i for i in range(0, num_bitmaps + 1)]).value_counts()
    #     percentage_categories = pd.Series(np.cumsum(categories.sort_index()).astype(np.double) /
    #                                       self.tenants['group_count'] * 100)
    #     if self.log_dir is not None:
    #         percentage_categories.to_csv(self.log_dir + "/percentage_of_groups_covered_with_varying_bitmaps.csv")
    #     return percentage_categories

    def groups_covered_with_bitmaps_only(self):
        _groups_covered_with_bitmaps_only = 0
        _groups_covered_with_bitmaps_only_without_default_bitmap = 0

        for t in bar_range(self.num_tenants, desc='data:groups_covered_with_bitmaps_only:'):
            tenant_maps = self.tenants_maps[t]
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']

            for g in range(group_count):
                group_map = groups_map[g]
                nodes_map = group_map['leafs_map'] if self.node_type == 'leafs' else group_map['pods_map']

                has_rule = reduce(lambda x, y: x | y, ['has_rule' in nodes_map[n] for n in nodes_map])
                if not has_rule:
                    _groups_covered_with_bitmaps_only += 1

                    if ('%s_default_bitmap' % self.node_type) not in group_map:
                        _groups_covered_with_bitmaps_only_without_default_bitmap += 1
                    else:
                        if group_map['%s_default_bitmap' % self.node_type] == 0:
                            _groups_covered_with_bitmaps_only_without_default_bitmap += 1

        df_groups_covered_with_bitmaps_only = pd.DataFrame()
        df_groups_covered_with_bitmaps_only['bitmaps'] = pd.Series(_groups_covered_with_bitmaps_only)
        df_groups_covered_with_bitmaps_only['bitmaps_without_default_bitmap'] = \
            pd.Series(_groups_covered_with_bitmaps_only_without_default_bitmap)

        if self.log_dir is not None:
            df_groups_covered_with_bitmaps_only.to_csv(
                self.log_dir + "/groups_covered_with_bitmaps_only_for_%s.csv" % self.node_type, index=False)

        return df_groups_covered_with_bitmaps_only

    def rule_count(self):
        _rule_count = pd.Series(self.optimizer['rules_count'])

        if self.log_dir is not None:
            _rule_count.to_csv(self.log_dir + "/rule_count_for_%s.csv" % self.node_type)

        return _rule_count

    def traffic_overhead_per_group_per_tenant(self):
        _traffic_overhead_per_group_per_tenant = []

        for t in bar_range(self.num_tenants, desc='data:traffic_overhead_per_group_per_tenant:'):
            tenant_maps = self.tenants_maps[t]
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']

            for g in range(group_count):
                group_map = groups_map[g]
                nodes_map = group_map['leafs_map'] if self.node_type == 'leafs' else group_map['pods_map']
                _actual_traffic = 0
                _redundant_traffic = 0

                for n in nodes_map:
                    node_map = nodes_map[n]
                    _actual_traffic += popcount(node_map['bitmap'])

                    if '~bitmap' in node_map:
                        _redundant_traffic += popcount(node_map['~bitmap'])

                _traffic_overhead_per_group_per_tenant += [_redundant_traffic / _actual_traffic]

        _traffic_overhead_per_group_per_tenant = pd.Series(_traffic_overhead_per_group_per_tenant)

        if self.log_dir is not None:
            _traffic_overhead_per_group_per_tenant.to_csv(
                self.log_dir + "/traffic_overhead_per_group_per_tenant_for_%s.csv" % self.node_type)

        return _traffic_overhead_per_group_per_tenant

#     def traffic_stats(self):
#         _actual_traffic_per_leaf = dict()
#         _unwanted_traffic_per_leaf = dict()
#
#         for l in range(self.num_leafs):
#             _actual_traffic_per_leaf[l] = [0] * self.num_hosts_per_leaf
#             _unwanted_traffic_per_leaf[l] = [0] * self.num_hosts_per_leaf
#
#         for t in bar_range(self.num_tenants, desc='data:traffic_stats:'):
#             tenant_maps = self.tenants_maps[t]
#             group_count = tenant_maps['group_count']
#             groups_map = tenant_maps['groups_map']
#
#             for g in range(group_count):
#                 group_map = groups_map[g]
#                 leafs_map = group_map['leafs_map']
#
#                 for l in leafs_map:
#                     leaf_map = leafs_map[l]
#                     for i, b in enumerate(bin(leaf_map['bitmap'])[:1:-1]):
#                         if b == '1':
#                             _actual_traffic_per_leaf[l][i] += 1
#
#                     if '~bitmap' in leaf_map:
#                         for i, b in enumerate(bin(leaf_map['~bitmap'])[:1:-1]):
#                             if b == '1':
#                                 _unwanted_traffic_per_leaf[l][i] += 1
#
#         return _actual_traffic_per_leaf, _unwanted_traffic_per_leaf
#
#     def traffic_overhead(self, actual_traffic_per_leaf, unwanted_traffic_per_leaf):
#         _actual_traffic_per_leaf = 0
#         for l in actual_traffic_per_leaf:
#             _actual_traffic_per_leaf += sum(actual_traffic_per_leaf[l])
#
#         _unwanted_traffic_per_leaf = 0
#         for l in unwanted_traffic_per_leaf:
#             _unwanted_traffic_per_leaf += sum(unwanted_traffic_per_leaf[l])
#
#         _traffic_overhead = pd.Series((_unwanted_traffic_per_leaf / _actual_traffic_per_leaf))
#
#         if self.log_dir is not None:
#             _traffic_overhead.to_csv(self.log_dir + "/traffic_overhead.csv")
#
#         return _traffic_overhead
#
#     def actual_traffic_per_link(self, traffic_per_leaf):
#         _traffic_per_link = []
#         for l in traffic_per_leaf:
#             _traffic_per_link += traffic_per_leaf[l]
#         _traffic_per_link = pd.Series(_traffic_per_link)
#
#         if self.log_dir is not None:
#             _traffic_per_link.to_csv(self.log_dir + "/actual_traffic_per_link.csv")
#
#         return _traffic_per_link
#
#     def unwanted_traffic_per_link(self, traffic_per_leaf):
#         _traffic_per_link = []
#         for l in traffic_per_leaf:
#             _traffic_per_link += traffic_per_leaf[l]
#         _traffic_per_link = pd.Series(_traffic_per_link)
#
#         if self.log_dir is not None:
#             _traffic_per_link.to_csv(self.log_dir + "/unwanted_traffic_per_link.csv")
#
#         return _traffic_per_link
#
#     def total_traffic_per_link(self, actual_traffic_per_leaf, unwanted_traffic_per_leaf):
#         _total_traffic_per_leaf = dict()
#         for l in actual_traffic_per_leaf:
#             if l in unwanted_traffic_per_leaf:
#                 _total_traffic_per_leaf[l] = [0] * self.num_hosts_per_leaf
#                 for i in range(self.num_hosts_per_leaf):
#                     _total_traffic_per_leaf[l][i] = (actual_traffic_per_leaf[l][i] +
#                                                      unwanted_traffic_per_leaf[l][i])
#             else:
#                 _total_traffic_per_leaf[l] = actual_traffic_per_leaf[l]
#
#         _total_traffic_per_link = []
#         for l in _total_traffic_per_leaf:
#             _total_traffic_per_link += _total_traffic_per_leaf[l]
#         _total_traffic_per_link = pd.Series(_total_traffic_per_link)
#
#         if self.log_dir is not None:
#             _total_traffic_per_link.to_csv(self.log_dir + "/total_traffic_per_link.csv")
#
#         return _total_traffic_per_link
#
#     # def traffic_overhead_per_link(self, total_traffic_per_link, actual_traffic_per_link):
#     #     link_count = len(total_traffic_per_link)
#     #     _traffic_overhead_per_link = [0] * link_count
#     #     for i in bar_range(link_count, desc='data:traffic_overhead_per_link:'):
#     #         if total_traffic_per_link[i] != 0:
#     #             _traffic_overhead_per_link[i] = ((total_traffic_per_link[i] - actual_traffic_per_link[i]) /
#     #                                              actual_traffic_per_link[i])
#     #     _traffic_overhead_per_link = pd.Series(_traffic_overhead_per_link)
#     #
#     #     if self.log_dir is not None:
#     #         _traffic_overhead_per_link.to_csv(self.log_dir + "/traffic_overhead_per_link.csv")
#     #     return _traffic_overhead_per_link
#
#     def leaf_spine_traffic_per_group_per_tenant_for_multicast(self):
#         _leaf_spine_traffic_per_group_per_tenant_for_multicast = []
#
#         for t in bar_range(self.num_tenants, desc='data:leaf_spine_traffic_per_group_per_tenant_for_multicast:'):
#             tenant_maps = self.tenants_maps[t]
#             group_count = tenant_maps['group_count']
#             groups_map = tenant_maps['groups_map']
#
#             for g in range(group_count):
#                 group_map = groups_map[g]
#                 leafs_map = group_map['leafs_map']
#                 _traffic = 0
#
#                 for l in leafs_map:
#                     leaf_map = leafs_map[l]
#                     _traffic += popcount(leaf_map['bitmap'])
#
#                 _leaf_spine_traffic_per_group_per_tenant_for_multicast += [2 + len(leafs_map) + _traffic]
#
#         _leaf_spine_traffic_per_group_per_tenant_for_multicast = \
#             pd.Series(_leaf_spine_traffic_per_group_per_tenant_for_multicast)
#
#         # if self.log_dir is not None:
#         #     _leaf_spine_traffic_per_group_per_tenant_for_multicast.to_csv(
#         #         self.log_dir + "/leaf_spine_traffic_per_group_per_tenant_for_multicast.csv")
#
#         return _leaf_spine_traffic_per_group_per_tenant_for_multicast
#
#     def leaf_spine_traffic_per_group_per_tenant_for_unicast(self):
#         _leaf_spine_traffic_per_group_per_tenant_for_unicast = []
#
#         for t in bar_range(self.num_tenants, desc='data:leaf_spine_traffic_per_group_per_tenant_for_unicast:'):
#             tenant_maps = self.tenants_maps[t]
#             group_count = tenant_maps['group_count']
#             groups_map = tenant_maps['groups_map']
#
#             for g in range(group_count):
#                 group_map = groups_map[g]
#                 leafs_map = group_map['leafs_map']
#                 _traffic = 0
#
#                 for l in leafs_map:
#                     leaf_map = leafs_map[l]
#                     _traffic += popcount(leaf_map['bitmap'])
#
#                 _leaf_spine_traffic_per_group_per_tenant_for_unicast += [4 * _traffic]
#
#         _leaf_spine_traffic_per_group_per_tenant_for_unicast = \
#             pd.Series(_leaf_spine_traffic_per_group_per_tenant_for_unicast)
#
#         # if self.log_dir is not None:
#         #     _leaf_spine_traffic_per_group_per_tenant_for_unicast.to_csv(
#         #         self.log_dir + "/leaf_spine_traffic_per_group_per_tenant_for_unicast.csv")
#
#         return _leaf_spine_traffic_per_group_per_tenant_for_unicast
#
#     def leaf_spine_traffic_per_group_per_tenant_for_overlay(self):
#         _leaf_spine_traffic_per_group_per_tenant_for_overlay = []
#
#         for t in bar_range(self.num_tenants, desc='data:leaf_spine_traffic_per_group_per_tenant_for_overlay:'):
#             tenant_maps = self.tenants_maps[t]
#             group_count = tenant_maps['group_count']
#             groups_map = tenant_maps['groups_map']
#
#             for g in range(group_count):
#                 group_map = groups_map[g]
#                 leafs_map = group_map['leafs_map']
#                 _traffic = 0
#
#                 for l in leafs_map:
#                     leaf_map = leafs_map[l]
#                     leaf_host_count = popcount(leaf_map['bitmap'])
#                     _traffic += 2 * (leaf_host_count - 1)
#
#                 _leaf_spine_traffic_per_group_per_tenant_for_overlay += [(4 * len(leafs_map)) + _traffic]
#
#         _leaf_spine_traffic_per_group_per_tenant_for_overlay = \
#             pd.Series(_leaf_spine_traffic_per_group_per_tenant_for_overlay)
#
#         # if self.log_dir is not None:
#         #     _leaf_spine_traffic_per_group_per_tenant_for_overlay.to_csv(
#         #         self.log_dir + "/leaf_spine_traffic_per_group_per_tenant_for_overlay.csv")
#
#         return _leaf_spine_traffic_per_group_per_tenant_for_overlay
#
#     def leaf_spine_traffic_per_group_per_tenant_for_baseerat(self):
#         _leaf_spine_traffic_per_group_per_tenant_for_baseerat = []
#
#         for t in bar_range(self.num_tenants, desc='data:leaf_spine_traffic_per_group_per_tenant_for_baseerat:'):
#             tenant_maps = self.tenants_maps[t]
#             group_count = tenant_maps['group_count']
#             groups_map = tenant_maps['groups_map']
#
#             for g in range(group_count):
#                 group_map = groups_map[g]
#                 leafs_map = group_map['leafs_map']
#                 _traffic = 0
#
#                 for l in leafs_map:
#                     leaf_map = leafs_map[l]
#                     _traffic += popcount(leaf_map['bitmap'])
#
#                     if '~bitmap' in leaf_map:
#                         _traffic += popcount(leaf_map['~bitmap'])
#
#                 _leaf_spine_traffic_per_group_per_tenant_for_baseerat += [2 + len(leafs_map) + _traffic]
#
#         _leaf_spine_traffic_per_group_per_tenant_for_baseerat = \
#             pd.Series(_leaf_spine_traffic_per_group_per_tenant_for_baseerat)
#
#         # if self.log_dir is not None:
#         #     _leaf_spine_traffic_per_group_per_tenant_for_baseerat.to_csv(
#         #         self.log_dir + "/leaf_spine_traffic_per_group_per_tenant_for_baseerat.csv")
#
#         return _leaf_spine_traffic_per_group_per_tenant_for_baseerat
#
#     def leaf_spine_traffic_per_group_per_tenant(self):
#         if self.log_dir:
#             t_dataframe = pd.DataFrame()
#             t_dataframe['multicast'] = self.leaf_spine_traffic_per_group_per_tenant_for_multicast()
#             t_dataframe['unicast'] = self.leaf_spine_traffic_per_group_per_tenant_for_unicast()
#             t_dataframe['overlay'] = self.leaf_spine_traffic_per_group_per_tenant_for_overlay()
#             t_dataframe['baseerat'] = self.leaf_spine_traffic_per_group_per_tenant_for_baseerat()
#             t_dataframe.to_csv(self.log_dir + "/leaf_spine_traffic_per_group_per_tenant.csv")

    def _log_cloud_stats(self):
        self.vm_count_per_tenant()
        self.group_count_per_tenant()
        self.group_size_per_group_per_tenant()
        self.leaf_count_per_group_per_tenant()
        self.pod_count_per_group_per_tenant()
        # at_dict, ut_dict = self.traffic_stats()
        # self.traffic_overhead(at_dict, ut_dict)
        # at_list = self.actual_traffic_per_link(at_dict)
        # ut_list = self.unwanted_traffic_per_link(ut_dict)
        # tt_list = self.total_traffic_per_link(at_dict, ut_dict)
        # # self.traffic_overhead_per_link(tt_list, at_list)
        # self.leaf_spine_traffic_per_group_per_tenant()

    def _log_optimizer_stats(self):
        self.algorithm_elapse_time()
        self.groups_covered_with_bitmaps_only()
        self.rule_count()
        self.traffic_overhead_per_group_per_tenant()

    def log_stats(self, log_cloud=True):
        if log_cloud:
            self._log_cloud_stats()
        self._log_optimizer_stats()


# class DynamicData:
#     def __init__(self, data, log_dir=None):
#         self.log_dir = log_dir
#
#         self.dynamic = data['dynamic']
#
#     def switch_event_types_to_update_count(self):
#         _switch_event_types_to_update_count = self.dynamic['switch_event_types_to_update_count']
#
#         virtual_join_dataframe = pd.DataFrame()
#         virtual_join_dataframe['updates'] = _switch_event_types_to_update_count['virtual']['J']
#         virtual_join_dataframe['switch'] = 'virtual'
#         virtual_join_dataframe['event'] = 'join'
#
#         virtual_leave_dataframe = pd.DataFrame()
#         virtual_leave_dataframe['updates'] = _switch_event_types_to_update_count['virtual']['L']
#         virtual_leave_dataframe['switch'] = 'virtual'
#         virtual_leave_dataframe['event'] = 'leave'
#
#         leaf_join_dataframe = pd.DataFrame()
#         leaf_join_dataframe['updates'] = _switch_event_types_to_update_count['leaf']['J']
#         leaf_join_dataframe['switch'] = 'leaf'
#         leaf_join_dataframe['event'] = 'join'
#
#         leaf_leave_dataframe = pd.DataFrame()
#         leaf_leave_dataframe['updates'] = _switch_event_types_to_update_count['leaf']['L']
#         leaf_leave_dataframe['switch'] = 'leaf'
#         leaf_leave_dataframe['event'] = 'leave'
#
#         t_dataframe = pd.concat([virtual_join_dataframe, virtual_leave_dataframe,
#                                  leaf_join_dataframe, leaf_leave_dataframe])
#
#         if self.log_dir:
#             t_dataframe.to_csv(self.log_dir + "/switch_event_types_to_update_count.csv")
#
#         return t_dataframe
#
#     def switch_event_types_to_update_count_normalized(self, switch_event_types_to_update_count):
#         _switch_event_types_to_group_size = self.dynamic['switch_event_types_to_group_size']
#         _switch_event_types_to_group_size_join_series = pd.Series(_switch_event_types_to_group_size['J'])
#         _switch_event_types_to_group_size_leave_series = pd.Series(_switch_event_types_to_group_size['L'])
#
#         t_dataframe = switch_event_types_to_update_count
#         t_dataframe['updates'] = 1.0 * t_dataframe['updates'] / pd.concat(
#             [_switch_event_types_to_group_size_join_series,
#              _switch_event_types_to_group_size_leave_series,
#              _switch_event_types_to_group_size_join_series,
#              _switch_event_types_to_group_size_leave_series])
#
#         if self.log_dir:
#             t_dataframe.to_csv(self.log_dir + "/switch_event_types_to_update_count_normalized.csv")
#
#         return t_dataframe
#
#     def log(self):
#         t_dataframe = self.switch_event_types_to_update_count()
#         self.switch_event_types_to_update_count_normalized(t_dataframe)
