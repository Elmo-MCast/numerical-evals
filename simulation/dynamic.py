from timeit import default_timer as timer
import numpy as np
from functools import reduce
import random
from simulation.algorithms import algorithms
from simulation.utils import bar_range


VM_TYPES = ['Pub', 'Sub', 'Both']

class Dynamic:
    def __init__(self, data, num_tenants=576, num_events=10000):
        self.data = data
        self.num_tenants = num_tenants
        self.num_events = num_events

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
            for group_map in tenant_maps['groups_map']:
                event_count = int(group_map['size'] / _sum_of_group_sizes * self.num_events)
                group_map['event_count'] = event_count

    def _get_tenant_group_vms_to_types_map(self):
        for t in bar_range(self.num_tenants, desc='tenants:groups:vms->type'):
            tenant_maps = self.tenants_maps[t]
            for group_map in tenant_maps['groups_map']:
                if 'vms_types' not in group_map:
                    group_map['vms_types'] = dict()

                vms_types = group_map['vms_types']
                for vm in group_map['vms']:
                    vms_types[vm] = random.choice(VM_TYPES[1:])
