import random
import pandas as pd
from simulation.event import Event
from simulation.utils import bar_range


# VM_TYPES = ['P',  # publisher
#             'S',  # subscriber
#             'B'   # Both
#             ]


class Dynamic:
    def __init__(self, data, num_tenants, num_events, algorithm, num_bitmaps,
                 num_leafs_per_bitmap, redundancy_per_bitmap, num_rules_per_leaf, probability,
                 min_group_size, num_hosts_per_leaf, debug=False):
        self.data = data
        self.num_tenants = num_tenants
        self.num_events = num_events
        self.algorithm = algorithm
        self.num_bitmaps = num_bitmaps
        self.num_leafs_per_bitmap = num_leafs_per_bitmap
        self.redundancy_per_bitmap = redundancy_per_bitmap
        self.num_rules_per_leaf = num_rules_per_leaf
        self.probability = probability
        self.min_group_size = min_group_size
        self.num_hosts_per_leaf = num_hosts_per_leaf
        self.debug = debug

        self.tenants = self.data['tenants']
        self.tenants_maps = self.tenants['maps']

        self.optimizer = self.data['optimizer']
        self.leafs_to_rules_count_map = self.optimizer['leafs_to_rules_count']

        self.data['dynamic'] = {'switch_event_types_to_update_count': {'virtual': {'J': [], 'L': []},
                                                                       'leaf': {'J': [], 'L': []}},
                                'switch_event_types_to_group_size': {'J': [], 'L': []}}
        self.dynamic = self.data['dynamic']
        self.switch_event_types_to_update_count_map = self.dynamic['switch_event_types_to_update_count']
        self.switch_event_types_to_group_size_map = self.dynamic['switch_event_types_to_group_size']

        self._get_tenant_groups_to_event_count_map()
        self._get_tenant_group_vms_to_types_map()
        self._run()

        if self.debug:
            print(pd.Series(self.switch_event_types_to_update_count_map['virtual']['J']).describe())
            print(pd.Series(self.switch_event_types_to_update_count_map['virtual']['L']).describe())
            print(pd.Series(self.switch_event_types_to_update_count_map['leaf']['J']).describe())
            print(pd.Series(self.switch_event_types_to_update_count_map['leaf']['L']).describe())

    def _get_tenant_groups_to_event_count_map(self):
        _sum_of_group_sizes = sum([group_map['size'] for t in range(self.num_tenants)
                                   for group_map in self.tenants_maps[t]['groups_map']])

        for t in bar_range(self.num_tenants, desc='tenants:groups->event count'):
            tenant_maps = self.tenants_maps[t]
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']
            for g in range(group_count):
                group_map = groups_map[g]
                event_count = int(group_map['size'] / _sum_of_group_sizes * self.num_events)
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

    def _run(self):
        for t in bar_range(self.num_tenants, desc='dynamic:%s' % self.algorithm):
            tenant_maps = self.tenants_maps[t]
            vm_count = tenant_maps['vm_count']
            vms_map = tenant_maps['vms_map']
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']
            for g in range(group_count):
                Event(self.switch_event_types_to_update_count_map, self.switch_event_types_to_group_size_map, vms_map,
                      self.algorithm, self.leafs_to_rules_count_map, self.num_bitmaps, self.num_leafs_per_bitmap,
                      self.redundancy_per_bitmap, self.num_rules_per_leaf, self.probability, groups_map[g],
                      self.min_group_size, vm_count, self.num_hosts_per_leaf)
