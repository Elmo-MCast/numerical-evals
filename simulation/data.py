import pandas as pd
from functools import reduce
from simulation.utils import bar_range, popcount


class Data:
    def __init__(self, data, num_tenants=3000, num_cores=4, num_pods=12, num_spines_per_pod=4, num_leafs_per_pod=48,
                 num_hosts_per_leaf=48, log_dir=None, node_type_0='pods', node_type_1=None):
        self.num_tenants = num_tenants
        self.num_cores = num_cores
        self.num_pods = num_pods
        self.num_spines_per_pod = num_spines_per_pod
        self.num_leafs_per_pod = num_leafs_per_pod
        self.num_hosts_per_leaf = num_hosts_per_leaf
        self.log_dir = log_dir
        self.node_type_0 = node_type_0
        self.node_type_1 = node_type_1

        self.tenants = data['tenants']
        self.tenants_maps = self.tenants['maps']

        self.optimizer = data['optimizer']

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

    def algorithm_elapse_time(self, node_type):
        _algorithm_elapse_time = pd.Series(self.optimizer[node_type]['algorithm_elapse_time'])

        if self.log_dir is not None:
            _algorithm_elapse_time.to_csv(self.log_dir + "/%s_algorithm_elapse_time.csv" % node_type, index=False)

        return _algorithm_elapse_time

    # def percentage_of_groups_covered_with_varying_bitmaps(self, num_bitmaps):
    #     categories = pd.cut(self.leafs_for_all_groups_for_all_tenants(), [i for i in range(-1, num_bitmaps + 1)],
    #                         right=True, labels=[i for i in range(0, num_bitmaps + 1)]).value_counts()
    #     percentage_categories = pd.Series(np.cumsum(categories.sort_index()).astype(np.double) /
    #                                       self.tenants['group_count'] * 100)
    #     if self.log_dir is not None:
    #         percentage_categories.to_csv(self.log_dir + "/percentage_of_groups_covered_with_varying_bitmaps.csv")
    #     return percentage_categories

    def groups_covered_with_bitmaps_only(self, node_type):
        _groups_covered_with_bitmaps_only = 0
        _groups_covered_with_bitmaps_only_without_default_bitmap = 0

        for t in bar_range(self.num_tenants, desc='data:groups_covered_with_bitmaps_only:'):
            tenant_maps = self.tenants_maps[t]
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']

            for g in range(group_count):
                group_map = groups_map[g]
                nodes_map = group_map['leafs_map'] if node_type == 'leafs' else group_map['pods_map']

                has_rule = reduce(lambda x, y: x | y, ['has_rule' in nodes_map[n] for n in nodes_map])
                if not has_rule:
                    _groups_covered_with_bitmaps_only += 1

                    if ('%s_default_bitmap' % node_type) not in group_map:
                        _groups_covered_with_bitmaps_only_without_default_bitmap += 1
                    else:
                        if group_map['%s_default_bitmap' % node_type] == 0:
                            _groups_covered_with_bitmaps_only_without_default_bitmap += 1

        df_groups_covered_with_bitmaps_only = pd.DataFrame()
        df_groups_covered_with_bitmaps_only['bitmaps'] = pd.Series(_groups_covered_with_bitmaps_only)
        df_groups_covered_with_bitmaps_only['bitmaps_without_default_bitmap'] = \
            pd.Series(_groups_covered_with_bitmaps_only_without_default_bitmap)

        if self.log_dir is not None:
            df_groups_covered_with_bitmaps_only.to_csv(
                self.log_dir + "/groups_covered_with_bitmaps_only_for_%s.csv" % node_type, index=False)

        return df_groups_covered_with_bitmaps_only

    def rule_count(self, node_type):
        _rule_count = pd.Series(self.optimizer[node_type]['rules_count'])

        if self.log_dir is not None:
            _rule_count.to_csv(self.log_dir + "/rule_count_for_%s.csv" % node_type, index=False)

        return _rule_count

    def traffic_overhead_per_group_per_tenant(self, node_type):
        _traffic_overhead_per_group_per_tenant = []

        for t in bar_range(self.num_tenants, desc='data:traffic_overhead_per_group_per_tenant:'):
            tenant_maps = self.tenants_maps[t]
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']

            for g in range(group_count):
                group_map = groups_map[g]
                nodes_map = group_map['leafs_map'] if node_type == 'leafs' else group_map['pods_map']
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
                self.log_dir + "/traffic_overhead_per_group_per_tenant_for_%s.csv" % node_type, index=False)

        return _traffic_overhead_per_group_per_tenant

    def traffic_per_group_per_tenant_for_multicast(self):
        _traffic_per_group_per_tenant_for_multicast = []

        for t in bar_range(self.num_tenants, desc='data:traffic_per_group_per_tenant_for_multicast:'):
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

                _traffic_per_group_per_tenant_for_multicast += [3 + len(pods_map) + len(leafs_map) + leafs_traffic]

        _traffic_per_group_per_tenant_for_multicast = \
            pd.Series(_traffic_per_group_per_tenant_for_multicast)

        return _traffic_per_group_per_tenant_for_multicast

    def traffic_per_group_per_tenant_for_unicast(self):
        _traffic_per_group_per_tenant_for_unicast = []

        for t in bar_range(self.num_tenants, desc='data:traffic_per_group_per_tenant_for_unicast:'):
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

                _traffic_per_group_per_tenant_for_unicast += [6 * leafs_traffic]

        _traffic_per_group_per_tenant_for_unicast = \
            pd.Series(_traffic_per_group_per_tenant_for_unicast)

        return _traffic_per_group_per_tenant_for_unicast

    def traffic_per_group_per_tenant_for_overlay(self):
        traffic_per_group_per_tenant_for_overlay = []

        for t in bar_range(self.num_tenants, desc='data:traffic_per_group_per_tenant_for_overlay:'):
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

                traffic_per_group_per_tenant_for_overlay += [(6 * len(leafs_map)) + leafs_traffic]

        traffic_per_group_per_tenant_for_overlay = \
            pd.Series(traffic_per_group_per_tenant_for_overlay)

        return traffic_per_group_per_tenant_for_overlay

    def traffic_per_group_per_tenant_for_overlay_corrected(self):
        traffic_per_group_per_tenant_for_overlay_corrected = []

        for t in bar_range(self.num_tenants, desc='data:traffic_per_group_per_tenant_for_overlay_corrected:'):
            tenant_maps = self.tenants_maps[t]
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']

            for g in range(group_count):
                group_map = groups_map[g]
                leafs_map = group_map['leafs_map']
                pods_map = group_map['pods_map']
                pods_traffic = 0
                leafs_traffic = 0

                for p in pods_map:
                    pod_map = pods_map[p]
                    pod_leaf_count = popcount(pod_map['bitmap'])
                    pods_traffic += 4 * (pod_leaf_count - 1)

                for l in leafs_map:
                    leaf_map = leafs_map[l]
                    leaf_host_count = popcount(leaf_map['bitmap'])
                    leafs_traffic += 2 * (leaf_host_count - 1)

                traffic_per_group_per_tenant_for_overlay_corrected += [
                    (6 * len(pods_map)) + pods_traffic + leafs_traffic]

        traffic_per_group_per_tenant_for_overlay_corrected = \
            pd.Series(traffic_per_group_per_tenant_for_overlay_corrected)

        return traffic_per_group_per_tenant_for_overlay_corrected

    def traffic_per_group_per_tenant_for_overlay_corrected_params(self):
        traffic_per_group_per_tenant_for_overlay_pods = []
        traffic_per_group_per_tenant_for_overlay_leafs = []
        traffic_per_group_per_tenant_for_overlay_pods_traffic = []

        for t in bar_range(self.num_tenants, desc='data:traffic_per_group_per_tenant_for_overlay_corrected_params:'):
            tenant_maps = self.tenants_maps[t]
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']

            for g in range(group_count):
                group_map = groups_map[g]
                leafs_map = group_map['leafs_map']
                pods_map = group_map['pods_map']
                pods_traffic = 0

                for p in pods_map:
                    pod_map = pods_map[p]
                    pod_leaf_count = popcount(pod_map['bitmap'])
                    pods_traffic += 4 * (pod_leaf_count - 1)

                traffic_per_group_per_tenant_for_overlay_pods += [len(pods_map)]
                traffic_per_group_per_tenant_for_overlay_leafs += [len(leafs_map)]
                traffic_per_group_per_tenant_for_overlay_pods_traffic += [pods_traffic]

        traffic_per_group_per_tenant_for_overlay_pods = \
            pd.Series(traffic_per_group_per_tenant_for_overlay_pods)
        traffic_per_group_per_tenant_for_overlay_leafs = \
            pd.Series(traffic_per_group_per_tenant_for_overlay_leafs)
        traffic_per_group_per_tenant_for_overlay_pods_traffic = \
            pd.Series(traffic_per_group_per_tenant_for_overlay_pods_traffic)

        return traffic_per_group_per_tenant_for_overlay_pods, \
               traffic_per_group_per_tenant_for_overlay_leafs, \
               traffic_per_group_per_tenant_for_overlay_pods_traffic

    def traffic_per_group_per_tenant_for_baseerat(self):
        _traffic_per_group_per_tenant_for_baseerat = []

        for t in bar_range(self.num_tenants, desc='data:traffic_per_group_per_tenant_for_baseerat:'):
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

                _traffic_per_group_per_tenant_for_baseerat += [3 + len(pods_map) + len(leafs_map) + leafs_traffic +
                                                               redundant_leafs + redundant_leafs_traffic]

        _traffic_per_group_per_tenant_for_baseerat = \
            pd.Series(_traffic_per_group_per_tenant_for_baseerat)

        return _traffic_per_group_per_tenant_for_baseerat

    def traffic_per_group_per_tenant_for_baseerat_bytes(self):
        _traffic_per_group_per_tenant_for_baseerat_bytes = []

        for t in bar_range(self.num_tenants, desc='data:traffic_per_group_per_tenant_for_baseerat_bytes:'):
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

                upstream_leaf_bits = self.num_hosts_per_leaf + self.num_spines_per_pod
                upstream_spine_bits = self.num_leafs_per_pod + self.num_cores
                core_bits = self.num_pods
                downstream_spine_bits = group_map['pods_header_size']
                downstream_leaf_bits = group_map['leafs_header_size']

                header_size_bits = (upstream_leaf_bits + upstream_spine_bits + core_bits +
                                    downstream_spine_bits + downstream_leaf_bits)

                host_to_leaf_edge_bits = header_size_bits
                leaf_to_spine_edge_bits = host_to_leaf_edge_bits - upstream_leaf_bits
                spine_to_core_edge_bits = leaf_to_spine_edge_bits - upstream_spine_bits
                core_to_spine_edge_bits = spine_to_core_edge_bits - core_bits
                spine_to_leaf_edge_bits = core_to_spine_edge_bits - downstream_spine_bits

                _traffic_per_group_per_tenant_for_baseerat_bytes += \
                    [(host_to_leaf_edge_bits +
                      leaf_to_spine_edge_bits +
                      spine_to_core_edge_bits +
                      (len(pods_map) * core_to_spine_edge_bits) +
                      (len(leafs_map) * spine_to_leaf_edge_bits) +
                      (redundant_leafs * spine_to_leaf_edge_bits)) / 8]

        _traffic_per_group_per_tenant_for_baseerat_bytes = \
            pd.Series(_traffic_per_group_per_tenant_for_baseerat_bytes)

        if self.log_dir is not None:
            _traffic_per_group_per_tenant_for_baseerat_bytes.to_csv(
                self.log_dir + "/traffic_per_group_per_tenant_for_baseerat_bytes.csv", index=False)

        return _traffic_per_group_per_tenant_for_baseerat_bytes

    def traffic_per_group_per_tenant(self):
        if self.log_dir:
            t_dataframe = pd.DataFrame()
            t_dataframe['multicast'] = self.traffic_per_group_per_tenant_for_multicast()
            t_dataframe['unicast'] = self.traffic_per_group_per_tenant_for_unicast()
            t_dataframe['overlay'] = self.traffic_per_group_per_tenant_for_overlay()
            t_dataframe['overlay_corrected'] = self.traffic_per_group_per_tenant_for_overlay_corrected()

            # traffic_per_group_per_tenant_for_overlay_pods, \
            # traffic_per_group_per_tenant_for_overlay_leafs, \
            # traffic_per_group_per_tenant_for_overlay_pods_traffic = \
            #     self.traffic_per_group_per_tenant_for_overlay_corrected_params()
            # t_dataframe['overlay_corrected_params:pods'] = traffic_per_group_per_tenant_for_overlay_pods
            # t_dataframe['overlay_corrected_params:leafs'] = traffic_per_group_per_tenant_for_overlay_leafs
            # t_dataframe['overlay_corrected_params:pods_traffic'] = traffic_per_group_per_tenant_for_overlay_pods_traffic

            t_dataframe['baseerat'] = self.traffic_per_group_per_tenant_for_baseerat()
            t_dataframe.to_csv(self.log_dir + "/traffic_per_group_per_tenant.csv", index=False)

    def _log_cloud_stats(self):
        self.vm_count_per_tenant()
        self.group_count_per_tenant()
        self.group_size_per_group_per_tenant()
        self.leaf_count_per_group_per_tenant()
        self.pod_count_per_group_per_tenant()

    def _log_optimizer_stats(self):
        self.algorithm_elapse_time(self.node_type_0)
        self.groups_covered_with_bitmaps_only(self.node_type_0)
        self.rule_count(self.node_type_0)
        self.traffic_overhead_per_group_per_tenant(self.node_type_0)

        if self.node_type_1:
            self.algorithm_elapse_time(self.node_type_1)
            self.groups_covered_with_bitmaps_only(self.node_type_1)
            self.rule_count(self.node_type_1)
            self.traffic_overhead_per_group_per_tenant(self.node_type_1)
            self.traffic_per_group_per_tenant()
            self.traffic_per_group_per_tenant_for_baseerat_bytes()

    def log_stats(self, log_cloud_stats=True):
        if log_cloud_stats:
            self._log_cloud_stats()
        self._log_optimizer_stats()



class DynamicData:
    def __init__(self, data, log_dir=None):
        self.log_dir = log_dir

        self.dynamic = data['dynamic']

    def switch_update_count(self):
        _switch_update_count = self.dynamic['switch_update_count']

        virtual_switch_join_dataframe = pd.DataFrame()
        virtual_switch_join_dataframe['updates'] = _switch_update_count['virtual']['J']
        virtual_switch_join_dataframe['switch'] = 'virtual'
        virtual_switch_join_dataframe['event'] = 'join'

        virtual_switch_leave_dataframe = pd.DataFrame()
        virtual_switch_leave_dataframe['updates'] = _switch_update_count['virtual']['L']
        virtual_switch_leave_dataframe['switch'] = 'virtual'
        virtual_switch_leave_dataframe['event'] = 'leave'

        leaf_switch_join_dataframe = pd.DataFrame()
        leaf_switch_join_dataframe['updates'] = _switch_update_count['leaf']['J']
        leaf_switch_join_dataframe['switch'] = 'leaf'
        leaf_switch_join_dataframe['event'] = 'join'

        leaf_switch_leave_dataframe = pd.DataFrame()
        leaf_switch_leave_dataframe['updates'] = _switch_update_count['leaf']['L']
        leaf_switch_leave_dataframe['switch'] = 'leaf'
        leaf_switch_leave_dataframe['event'] = 'leave'

        pod_switch_join_dataframe = pd.DataFrame()
        pod_switch_join_dataframe['updates'] = _switch_update_count['pod']['J']
        pod_switch_join_dataframe['switch'] = 'pod'
        pod_switch_join_dataframe['event'] = 'join'

        pod_switch_leave_dataframe = pd.DataFrame()
        pod_switch_leave_dataframe['updates'] = _switch_update_count['pod']['L']
        pod_switch_leave_dataframe['switch'] = 'pod'
        pod_switch_leave_dataframe['event'] = 'leave'

        t_dataframe = pd.concat([virtual_switch_join_dataframe, virtual_switch_leave_dataframe,
                                 leaf_switch_join_dataframe, leaf_switch_leave_dataframe,
                                 pod_switch_join_dataframe, pod_switch_leave_dataframe])

        if self.log_dir:
            t_dataframe.to_csv(self.log_dir + "/switch_update_count.csv", index=False)

        return t_dataframe

    def switch_update_count_normalized(self, switch_update_count):
        _switch_group_size = self.dynamic['switch_group_size']
        _switch_group_size_join_series = pd.Series(_switch_group_size['J'])
        _switch_group_size_leave_series = pd.Series(_switch_group_size['L'])

        t_dataframe = switch_update_count
        t_dataframe['updates'] = 1.0 * t_dataframe['updates'] / pd.concat(
            [_switch_group_size_join_series,
             _switch_group_size_leave_series,
             _switch_group_size_join_series,
             _switch_group_size_leave_series,
             _switch_group_size_join_series,
             _switch_group_size_leave_series])

        if self.log_dir:
            t_dataframe.to_csv(self.log_dir + "/switch_update_count_normalized.csv")

        return t_dataframe

    def per_switch_update_count(self):
        _per_switch_update_count = self.dynamic['per_switch_update_count']

        virtual_switch_dataframe = pd.DataFrame()
        virtual_switch_dataframe['updates'] = _per_switch_update_count['virtual']
        virtual_switch_dataframe['switch'] = 'virtual'

        leaf_switch_dataframe = pd.DataFrame()
        leaf_switch_dataframe['updates'] = _per_switch_update_count['leaf']
        leaf_switch_dataframe['switch'] = 'leaf'

        pod_switch_dataframe = pd.DataFrame()
        pod_switch_dataframe['updates'] = _per_switch_update_count['pod']
        pod_switch_dataframe['switch'] = 'pod'

        t_dataframe = pd.concat([virtual_switch_dataframe, leaf_switch_dataframe, pod_switch_dataframe])

        if self.log_dir:
            t_dataframe.to_csv(self.log_dir + "/per_switch_update_count.csv", index=False)

        return t_dataframe

    def with_failures(self):
        _with_failures = self.dynamic['with_failures']

        group_count = pd.Series(_with_failures['group_count'])

        per_switch_update_count = pd.DataFrame()
        per_switch_update_count['updates'] = _with_failures['per_virtual_switch_update_count']
        per_switch_update_count['switch'] = 'virtual'

        if self.log_dir:
            group_count.to_csv(self.log_dir + "/group_count.csv")
            per_switch_update_count.to_csv(self.log_dir + "/per_switch_update_count.csv", index=False)

        return group_count, per_switch_update_count

    def log(self):
        t_dataframe = self.switch_update_count()
        self.switch_update_count_normalized(t_dataframe)
        self.per_switch_update_count()
        self.with_failures()
