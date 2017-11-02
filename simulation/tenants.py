import random
import pandas as pd
from simulation.utils import bar_range


class Tenants:
    def __init__(self, data, max_vms_per_host=20, num_tenants=3000, min_vms=10, max_vms=5000, vm_dist='expon',
                 num_groups=100000, min_group_size=5, group_size_dist='uniform', debug=False):
        self.data = data
        self.num_tenants = num_tenants
        self.num_hosts = self.data['network']['num_hosts']
        self.max_vms_per_host = max_vms_per_host
        self.min_vms = min_vms
        self.max_vms = max_vms
        self.vm_dist = vm_dist
        self.num_groups = num_groups
        self.min_group_size = min_group_size
        self.group_size_dist = group_size_dist

        self.data['tenants'] = {'num_tenants': num_tenants,
                                'num_hosts': self.num_hosts,
                                'max_vms_per_host': max_vms_per_host,
                                'min_vms': min_vms,
                                'max_vms': max_vms,
                                'vm_dist': vm_dist,
                                'num_groups': num_groups,
                                'min_group_size': min_group_size,
                                'group_size_dist': group_size_dist,

                                'vm_count': 0,
                                'group_count': 0,
                                'maps': [{'vm_count': None,
                                          'group_count': None,
                                          'groups_map': None} for _ in range(self.num_tenants)]
                                }

        self.tenants = self.data['tenants']
        self.tenants_maps = self.tenants['maps']

        self._get_tenant_to_vm_count_map()
        print('tenants[vm_count]: initialized.')

        if debug:
            print(pd.Series([self.tenants_maps[t]['vm_count'] for t in range(self.num_tenants)]).describe())
            print("VM Count: %s" % self.tenants['vm_count'])

        self._get_tenant_to_group_count_map()
        print('tenants[group_count]: initialized.')

        if debug:
            print(pd.Series([self.tenants_maps[t]['group_count'] for t in range(self.num_tenants)]).describe())
            print("Sum: %s" % sum(pd.Series([self.tenants_maps[t]['group_count'] for t in range(self.num_tenants)])))

        for t in range(self.num_tenants):
            self.tenants_maps[t]['groups_map'] = \
                [{'size': None, 'vms': None} for _ in range(self.tenants_maps[t]['group_count'])]

        self._get_tenant_groups_to_sizes_map()
        print('tenants[groups_to_sizes]: initialized.')

        if debug:
            _group_sizes_for_all_tenants = []
            for t in range(self.tenants['num_tenants']):
                for g in range(self.tenants_maps[t]['group_count']):
                    _group_sizes_for_all_tenants += [self.tenants_maps[t]['groups_map'][g]['size']]
            print(pd.Series(_group_sizes_for_all_tenants).describe())

        self._get_tenant_groups_to_vms_map()
        print('tenants[groups_to_vms]: initialized.')

    def _get_tenant_to_vm_count_map(self):
        if self.vm_dist == 'expon':
            for t in range(self.num_tenants):
                sample = random.random()
                if sample < 0.02:
                    vm_count = random.randint(self.min_vms, self.max_vms)
                else:
                    vm_count = int((random.expovariate(4) / 10) * (self.max_vms - self.min_vms)) \
                               % (self.max_vms - self.min_vms) + self.min_vms

                self.tenants_maps[t]['vm_count'] = vm_count
                self.tenants['vm_count'] += vm_count
        else:
            raise (Exception("invalid dist parameter for vm allocation"))

    def _get_tenant_to_group_count_map(self):
        # ... weighted assignment of groups (based on VMs) to tenants
        for t in range(self.num_tenants):
            group_count = int(self.tenants_maps[t]['vm_count'] / self.tenants['vm_count'] * self.num_groups)
            self.tenants_maps[t]['group_count'] = int(group_count)
            self.tenants['group_count'] += int(group_count)

    def _get_tenant_groups_to_sizes_map(self):
        if self.group_size_dist == 'uniform':
            for t in range(self.num_tenants):
                for g in range(self.tenants_maps[t]['group_count']):
                    size = random.randint(self.min_group_size, self.tenants_maps[t]['vm_count'])
                    self.tenants_maps[t]['groups_map'][g]['size'] = size
        elif self.group_size_dist == 'wve':  # ... using mix3 distribution from the dcn-mcast paper.
            for t in range(self.num_tenants):
                for g in range(self.tenants_maps[t]['group_count']):
                    sample = random.random()
                    if sample < 0.02:
                        size = self.tenants_maps[t]['vm_count'] - \
                               int(random.gammavariate(2, 0.1) * self.tenants_maps[t]['vm_count'] / 15) \
                               % self.tenants_maps[t]['vm_count']
                    else:
                        size = int(random.gammavariate(2, 0.2) * self.tenants_maps[t]['vm_count'] / 15 +
                                   self.min_group_size - 1) % self.tenants_maps[t]['vm_count'] + 1
                    size = max(size, self.min_group_size)
                    self.tenants_maps[t]['groups_map'][g]['size'] = size
        else:
            raise (Exception("invalid dist parameter for group size allocation"))

    def _get_tenant_groups_to_vms_map(self):
        for t in bar_range(self.num_tenants, desc='vms'):
            for g in range(self.tenants_maps[t]['group_count']):
                self.tenants_maps[t]['groups_map'][g]['vms'] = random.sample(
                    range(self.tenants_maps[t]['vm_count']),
                    self.tenants_maps[t]['groups_map'][g]['size'])
