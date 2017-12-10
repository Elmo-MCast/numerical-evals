import random
import pandas as pd
from simulation.event import Event
from simulation.utils import bar_range


# VM_TYPES = ['P',  # publisher
#             'S',  # subscriber
#             'B'   # Both
#             ]


class Dynamic:
    def __init__(self, data, num_events, num_pods, num_leafs_per_pod, num_hosts_per_leaf, num_tenants, min_group_size,
                 pods_algorithm, pods_num_bitmaps, pods_num_nodes_per_bitmap, pods_redundancy_per_bitmap,
                 pods_num_rules, pods_probability, leafs_algorithm, leafs_num_bitmaps, leafs_num_nodes_per_bitmap,
                 leafs_redundancy_per_bitmap, leafs_num_rules, leafs_probability, debug=False):
        self.data = data
        self.num_events = num_events
        self.num_pods = num_pods
        self.num_leafs_per_pod = num_leafs_per_pod
        self.num_hosts_per_leaf = num_hosts_per_leaf
        self.num_tenants = num_tenants
        self.min_group_size = min_group_size
        self.pods_algorithm = pods_algorithm
        self.pods_num_bitmaps = pods_num_bitmaps
        self.pods_num_nodes_per_bitmap = pods_num_nodes_per_bitmap
        self.pods_redundancy_per_bitmap = pods_redundancy_per_bitmap
        self.pods_num_rules = pods_num_rules
        self.pods_probability = pods_probability
        self.leafs_algorithm = leafs_algorithm
        self.leafs_num_bitmaps = leafs_num_bitmaps
        self.leafs_num_nodes_per_bitmap = leafs_num_nodes_per_bitmap
        self.leafs_redundancy_per_bitmap = leafs_redundancy_per_bitmap
        self.leafs_num_rules = leafs_num_rules
        self.leafs_probability = leafs_probability
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
            'switch_group_size': {'J': [], 'L': []}}
        self.dynamic = self.data['dynamic']
        self.switch_update_count_map = self.dynamic['switch_update_count']
        self.switch_group_size_map = self.dynamic['switch_group_size']

        self._get_tenant_groups_to_event_count_map()
        self._get_tenant_group_vms_to_types_map()

        self.event = Event(self.switch_update_count_map, self.switch_group_size_map, self.num_pods,
                           self.num_leafs_per_pod, self.num_hosts_per_leaf, self.min_group_size, self.pods_algorithm,
                           self.pods_rules_count_map, self.pods_num_bitmaps, self.pods_num_nodes_per_bitmap,
                           self.pods_redundancy_per_bitmap, self.pods_num_rules, self.pods_probability,
                           self.leafs_algorithm, self.leafs_rules_count_map, self.leafs_num_bitmaps,
                           self.leafs_num_nodes_per_bitmap, self.leafs_redundancy_per_bitmap, self.leafs_num_rules,
                           self.leafs_probability)

        self._process()

        if self.debug:
            print(pd.Series(self.switch_update_count_map['virtual']['J']).describe())
            print(pd.Series(self.switch_update_count_map['virtual']['L']).describe())
            print(pd.Series(self.switch_update_count_map['leaf']['J']).describe())
            print(pd.Series(self.switch_update_count_map['leaf']['L']).describe())

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
