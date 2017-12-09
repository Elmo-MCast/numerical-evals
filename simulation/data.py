import pandas as pd
from functools import reduce
from simulation.utils import bar_range, popcount


class Data:
    def __init__(self, data, num_tenants=3000, num_pods=11, num_leafs_per_pod=48, num_hosts_per_leaf=48,
                 log_dir=None, node_type='leafs'):
        self.num_tenants = num_tenants
        self.num_pods = num_pods
        self.num_leafs_per_pod = num_leafs_per_pod
        self.num_hosts_per_leaf = num_hosts_per_leaf
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
            _rule_count.to_csv(self.log_dir + "/rule_count_for_%s.csv" % self.node_type, index=False)

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
                self.log_dir + "/traffic_overhead_per_group_per_tenant_for_%s.csv" % self.node_type, index=False)

        return _traffic_overhead_per_group_per_tenant

    def dc_traffic_per_group_per_tenant_for_multicast(self):
        _dc_traffic_per_group_per_tenant_for_multicast = []

        for t in bar_range(self.num_tenants, desc='data:dc_traffic_per_group_per_tenant_for_multicast:'):
            tenant_maps = self.tenants_maps[t]
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']

            for g in range(group_count):
                group_map = groups_map[g]
                leafs_map = group_map['leafs_map']
                pods_map = group_map['pods_map']
                leafs_traffic = 0

                for l in leafs_map:
                    leaf_map = leafs_map[l]
                    leafs_traffic += popcount(leaf_map['bitmap'])

                _dc_traffic_per_group_per_tenant_for_multicast += [3 + len(pods_map) + len(leafs_map) + leafs_traffic]

        _dc_traffic_per_group_per_tenant_for_multicast = \
            pd.Series(_dc_traffic_per_group_per_tenant_for_multicast)

        return _dc_traffic_per_group_per_tenant_for_multicast

    def dc_traffic_per_group_per_tenant_for_unicast(self):
        _dc_traffic_per_group_per_tenant_for_unicast = []

        for t in bar_range(self.num_tenants, desc='data:dc_traffic_per_group_per_tenant_for_unicast:'):
            tenant_maps = self.tenants_maps[t]
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']

            for g in range(group_count):
                group_map = groups_map[g]
                leafs_map = group_map['leafs_map']
                # pods_map = group_map['pods_map']
                leafs_traffic = 0

                for l in leafs_map:
                    leaf_map = leafs_map[l]
                    leafs_traffic += popcount(leaf_map['bitmap'])

                _dc_traffic_per_group_per_tenant_for_unicast += [6 * leafs_traffic]

        _dc_traffic_per_group_per_tenant_for_unicast = \
            pd.Series(_dc_traffic_per_group_per_tenant_for_unicast)

        return _dc_traffic_per_group_per_tenant_for_unicast

    def dc_traffic_per_group_per_tenant_for_overlay(self):
        _dc_traffic_per_group_per_tenant_for_overlay = []

        for t in bar_range(self.num_tenants, desc='data:dc_traffic_per_group_per_tenant_for_overlay:'):
            tenant_maps = self.tenants_maps[t]
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']

            for g in range(group_count):
                group_map = groups_map[g]
                leafs_map = group_map['leafs_map']
                # pods_map = group_map['pods_map']
                leafs_traffic = 0

                for l in leafs_map:
                    leaf_map = leafs_map[l]
                    leaf_host_count = popcount(leaf_map['bitmap'])
                    leafs_traffic += 2 * (leaf_host_count - 1)

                _dc_traffic_per_group_per_tenant_for_overlay += [(6 * len(leafs_map)) + leafs_traffic]

        _dc_traffic_per_group_per_tenant_for_overlay = \
            pd.Series(_dc_traffic_per_group_per_tenant_for_overlay)

        return _dc_traffic_per_group_per_tenant_for_overlay

    def dc_traffic_per_group_per_tenant_for_baseerat(self):
        _dc_traffic_per_group_per_tenant_for_baseerat = []

        for t in bar_range(self.num_tenants, desc='data:dc_traffic_per_group_per_tenant_for_baseerat:'):
            tenant_maps = self.tenants_maps[t]
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']

            for g in range(group_count):
                group_map = groups_map[g]
                leafs_map = group_map['leafs_map']
                pods_map = group_map['pods_map']
                leafs_traffic = 0
                redundant_leafs = 0
                redundant_leafs_traffic = 0

                for p in pods_map:
                    pod_map = pods_map[p]
                    if '~bitmap' in pod_map:
                        redundant_leafs += popcount(pod_map['~bitmap'])

                if 'leafs_default_bitmap' in group_map:
                    redundant_leafs_traffic = redundant_leafs * popcount(group_map['leafs_default_bitmap'])

                for l in leafs_map:
                    leaf_map = leafs_map[l]
                    leafs_traffic += popcount(leaf_map['bitmap'])
                    if '~bitmap' in leaf_map:
                        leafs_traffic += popcount(leaf_map['~bitmap'])

                _dc_traffic_per_group_per_tenant_for_baseerat += [3 + len(pods_map) + len(leafs_map) + leafs_traffic +
                                                                  redundant_leafs + redundant_leafs_traffic]

        _dc_traffic_per_group_per_tenant_for_baseerat = \
            pd.Series(_dc_traffic_per_group_per_tenant_for_baseerat)

        return _dc_traffic_per_group_per_tenant_for_baseerat

    def dc_traffic_per_group_per_tenant(self):
        if self.log_dir:
            t_dataframe = pd.DataFrame()
            t_dataframe['multicast'] = self.dc_traffic_per_group_per_tenant_for_multicast()
            t_dataframe['unicast'] = self.dc_traffic_per_group_per_tenant_for_unicast()
            t_dataframe['overlay'] = self.dc_traffic_per_group_per_tenant_for_overlay()
            t_dataframe['baseerat'] = self.dc_traffic_per_group_per_tenant_for_baseerat()
            t_dataframe.to_csv(self.log_dir + "/dc_traffic_per_group_per_tenant.csv", index=False)

    def _log_cloud_stats(self):
        self.vm_count_per_tenant()
        self.group_count_per_tenant()
        self.group_size_per_group_per_tenant()
        self.leaf_count_per_group_per_tenant()
        self.pod_count_per_group_per_tenant()

    def _log_optimizer_stats(self):
        self.algorithm_elapse_time()
        self.groups_covered_with_bitmaps_only()
        self.rule_count()
        self.traffic_overhead_per_group_per_tenant()
        self.dc_traffic_per_group_per_tenant()

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
