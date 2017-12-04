from timeit import default_timer as timer
import numpy as np
from functools import reduce
import random
from simulation.algorithms import algorithms
from simulation.utils import bar_range


# VM_TYPES = ['P',  # publisher
#             'S',  # subscriber
#             'B'   # Both
#             ]
# EVENT_TYPES = ['J',  # Join
#                'L'   # Leave
#                ]


class Dynamic:
    def __init__(self, data, num_tenants=576, num_events=10000, algorithm='single-match',
                 min_group_size=5):
        self.data = data
        self.num_tenants = num_tenants
        self.num_events = num_events
        self.algorithm = algorithm
        self.min_group_size = min_group_size

        self.tenants = self.data['tenants']
        self.tenants_maps = self.tenants['maps']

        self.optimizer = self.data['optimizer']
        self.leafs_to_rules_count = self.optimizer['leafs_to_rules_count']

        self._get_tenant_groups_to_event_count_map()
        self._get_tenant_group_vms_to_types_map()

        pass

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
        switch_event_types_to_count = {'virtual': {'J': [], 'L': []},
                                       'leaf_switch': {'J': [], 'L': []}}
        leaf_switch_event_types_to_count = {'J': [], 'L': []}
        for t in bar_range(self.num_tenants, desc='dynamic:%s' % self.algorithm):
            tenant_maps = self.tenants_maps[t]
            vm_count = tenant_maps['vm_count']
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']
            for g in range(group_count):
                group_map = groups_map[g]

                Event(switch_event_types_to_count,
                      group_map, self.min_group_size, vm_count)


class Event:
    def __init__(self, switch_event_types_to_count,
                 group, min_group_size, vm_count):
        self.virtual_switch_event_types_to_count = switch_event_types_to_count['virtual']
        self.leaf_switch_event_types_to_count = switch_event_types_to_count['leaf']
        self.group = group
        self.min_group_size = min_group_size
        self.vm_count = vm_count

        self._run()

    def _run(self):
        event_count = self.group['event_count']
        group_size = self.group['size']
        group_vms = self.group['vms']
        group_vms_types = self.group['vm_types']
        for e in range(event_count):
            # Get event type
            if group_size == self.min_group_size:
                event_type = 'J'
            elif group_size == self.vm_count:
                event_type = 'L'
            else:
                event_type = random.sample(['J', 'L'], 1)[0]

            self.virtual_switch_event_types_to_count[event_type] += [0]
            self.leaf_switch_event_types_to_count[event_type] += [0]

            if event_type == 'J':  # Process join event
                virtual_switch_event_type_to_count = self.virtual_switch_event_types_to_count[event_type]
                leaf_switch_event_type_to_count = self.leaf_switch_event_types_to_count[event_type]
                vm = random.sample(set(range(self.vm_count)) - set(group_vms), 1)[0]
                vm_type = random.sample(['P', 'S', 'B'], 1)[0]

                if vm_type == 'P':
                    virtual_switch_event_type_to_count[-1] += 1
                elif vm_type == 'S':
                    pass

                group_vms += [vm]
                group_vms_types[vm] = vm_type
            else:  # Process leave event
                virtual_switch_event_type_to_count = self.virtual_switch_event_types_to_count[event_type]
                leaf_switch_event_type_to_count = self.leaf_switch_event_types_to_count[event_type]
                vm = random.sample(group_vms, 1)[0]
                vm_type = group_vms_types[vm]

                if vm_type == 'P':
                    virtual_switch_event_type_to_count[-1] += 1

                group_vms.remove(vm)
                del group_vms_types[vm]




