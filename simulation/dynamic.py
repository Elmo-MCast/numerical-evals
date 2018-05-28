import random
import pandas as pd
from simulation.event import Event
from simulation.utils import bar_range
from math import ceil, log2


# VM_TYPES = ['P',  # publisher
#             'S',  # subscriber
#             'B'   # Both
#             ]


class Dynamic:
    def __init__(self, data, num_events, num_pods, num_leafs_per_pod, num_hosts_per_leaf, num_tenants, min_group_size,
                 pods_algorithm, pods_num_bitmaps, pods_num_nodes_per_bitmap, pods_redundancy_per_bitmap,
                 pods_num_rules, pods_probability, leafs_algorithm, leafs_num_bitmaps, leafs_num_nodes_per_bitmap,
                 leafs_redundancy_per_bitmap, leafs_num_rules, leafs_probability, with_failures=False,
                 failed_node_type='spine', num_spines_per_pod=None, debug=False):
        self.data = data
        self.num_events = num_events
        self.num_pods = num_pods
        self.num_leafs_per_pod = num_leafs_per_pod
        self.num_hosts_per_leaf = num_hosts_per_leaf
        self.num_leafs = num_pods * num_leafs_per_pod
        self.num_tenants = num_tenants
        self.num_hosts = self.num_leafs * num_hosts_per_leaf
        self.min_group_size = min_group_size
        self.pods_algorithm = pods_algorithm
        self.pods_num_bitmaps = pods_num_bitmaps
        self.pods_num_nodes_per_bitmap = pods_num_nodes_per_bitmap
        self.pods_redundancy_per_bitmap = pods_redundancy_per_bitmap
        self.pods_num_rules = pods_num_rules
        self.pods_probability = pods_probability
        self.pods_node_id_width = ceil(log2(self.num_pods))
        self.leafs_algorithm = leafs_algorithm
        self.leafs_num_bitmaps = leafs_num_bitmaps
        self.leafs_num_nodes_per_bitmap = leafs_num_nodes_per_bitmap
        self.leafs_redundancy_per_bitmap = leafs_redundancy_per_bitmap
        self.leafs_num_rules = leafs_num_rules
        self.leafs_probability = leafs_probability
        self.leafs_node_id_width = ceil(log2(self.num_leafs))
        self.with_failures = with_failures
        self.failed_node_type = failed_node_type
        self.num_spines_per_pod = num_spines_per_pod
        self.num_spines = num_pods * num_spines_per_pod
        self.debug = debug

        self.tenants = self.data['tenants']
        self.tenants_maps = self.tenants['maps']

        self.optimizer = self.data['optimizer']
        self.pods_rules_count_map = self.optimizer['pods']['rules_count']
        self.leafs_rules_count_map = self.optimizer['leafs']['rules_count']

        self.data['dynamic'] = {
            'switch_update_count':
                {'virtual': {'J': [], 'L': []},
                 'leaf': {'J': [], 'L': []},
                 'pod': {'J': [], 'L': []}
                 },
            'switch_group_size': {'J': [], 'L': []},
            'per_switch_update_count':
                {'virtual': [0] * self.num_hosts,
                 'leaf': [0] * self.num_leafs,
                 'pod': [0] * self.num_pods
                },
            'with_failures':
                {'group_count': 0,
                 'per_virtual_switch_update_count': [0] * self.num_hosts
                 }
        }
        self.dynamic = self.data['dynamic']
        self.switch_update_count_map = self.dynamic['switch_update_count']
        self.switch_group_size_map = self.dynamic['switch_group_size']
        self.per_switch_update_count_map = self.dynamic['per_switch_update_count']
        self.with_failures_map = self.dynamic['with_failures']

        self._get_tenant_groups_to_event_count_map()
        self._get_tenant_group_vms_to_types_map()

        self.event = Event(self.switch_update_count_map, self.switch_group_size_map, self.per_switch_update_count_map,
                           self.num_pods, self.num_leafs_per_pod, self.num_hosts_per_leaf, self.min_group_size,
                           self.pods_algorithm, self.pods_rules_count_map, self.pods_num_bitmaps,
                           self.pods_num_nodes_per_bitmap, self.pods_redundancy_per_bitmap, self.pods_num_rules,
                           self.pods_probability, self.pods_node_id_width, self.leafs_algorithm,
                           self.leafs_rules_count_map, self.leafs_num_bitmaps, self.leafs_num_nodes_per_bitmap,
                           self.leafs_redundancy_per_bitmap, self.leafs_num_rules, self.leafs_probability,
                           self.leafs_node_id_width, self.failed_node_type, self.num_spines_per_pod,
                           self.with_failures_map)

        if not self.with_failures:
            self._process()
        else:
            self._process_with_failures()

        if self.debug:
            print('Virtual switches:')
            print('----Join/Leave:')
            print(pd.Series(self.switch_update_count_map['virtual']['J']).describe())
            print(pd.Series(self.switch_update_count_map['virtual']['L']).describe())
            print('----Per switch updates:')
            print(pd.Series(self.per_switch_update_count_map['virtual']).describe())
            print('Leaf switches:')
            print('----Join/Leave:')
            print(pd.Series(self.switch_update_count_map['leaf']['J']).describe())
            print(pd.Series(self.switch_update_count_map['leaf']['L']).describe())
            print('----Per switch updates:')
            print(pd.Series(self.per_switch_update_count_map['leaf']).describe())
            print('Pod switches:')
            print('----Join/Leave:')
            print(pd.Series(self.switch_update_count_map['pod']['J']).describe())
            print(pd.Series(self.switch_update_count_map['pod']['L']).describe())
            print('----Per switch updates:')
            print(pd.Series(self.per_switch_update_count_map['pod']).describe())

            print('With Failures:')
            print('----Affected groups: %s' % (self.with_failures_map['group_count']))
            print('----Number of virtual switches updated: %s' % (sum(
                [1 for n in self.with_failures_map['per_virtual_switch_update_count'] if n > 0])))
            print('----Per switch updates:')
            print(pd.Series(self.with_failures_map['per_virtual_switch_update_count']).describe())

    def _get_tenant_groups_to_event_count_map(self):
        sum_of_group_sizes = sum([group_map['size'] for t in range(self.num_tenants)
                                  for group_map in self.tenants_maps[t]['groups_map']])

        for t in bar_range(self.num_tenants, desc='tenants:groups->event count'):
            tenant_maps = self.tenants_maps[t]
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']
            for g in range(group_count):
                group_map = groups_map[g]
                event_count = int(group_map['size'] / sum_of_group_sizes * self.num_events)
                group_map['event_count'] = event_count

    def _get_tenant_group_vms_to_types_map(self):
        for t in bar_range(self.num_tenants, desc='tenants:groups:vms->type'):
            tenant_maps = self.tenants_maps[t]
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']
            for g in range(group_count):
                group_map = groups_map[g]

                if 'vms_types' not in group_map:
                    group_map['vms_types'] = dict()
                vms_types = group_map['vms_types']
                for vm in group_map['vms']:
                    vms_types[vm] = random.sample(['S', 'B'], 1)[0]

    def _process(self):
        for t in bar_range(self.num_tenants, desc='dynamic'):
            tenant_maps = self.tenants_maps[t]
            vm_count = tenant_maps['vm_count']
            vm_to_host_map = tenant_maps['vm_to_host_map']
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']
            for g in range(group_count):
                self.event.process(vm_count, vm_to_host_map, groups_map[g])

    def _process_with_failures(self):
        self._process()

        failed_node = None
        if self.failed_node_type == 'spine':
            failed_node = random.sample(range(self.num_spines), 1)[0]

        for t in bar_range(self.num_tenants, desc='dynamic_with_failures'):
            tenant_maps = self.tenants_maps[t]
            vm_to_host_map = tenant_maps['vm_to_host_map']
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']
            for g in range(group_count):
                self.event.process_with_failures(failed_node, vm_to_host_map, groups_map[g])
