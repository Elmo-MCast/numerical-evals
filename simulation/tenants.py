import numpy as np
from scipy import stats


class Tenants:
    def __init__(self, data, max_vms_per_host=20, num_tenants=3000, min_vms=10, max_vms=5000, vm_dist='expon',
                 num_groups=100000, min_group_size=5, group_size_dist='uniform'):
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

        self._get_tenant_to_group_count_map()
        print('tenants[group_count]: initialized.')

        for t in range(self.num_tenants):
            self.tenants_maps[t]['groups_map'] = \
                [{'size': None, 'vms': None} for _ in range(self.tenants_maps[t]['group_count'])]

        self._get_tenant_groups_to_sizes_map()
        print('tenants[groups_to_sizes]: initialized.')

        self._get_tenant_groups_to_vms_map()
        print('tenants[groups_to_vms]: initialized.')

    def _get_tenant_to_vm_count_map(self):
        if self.vm_dist == 'geom':  # ... using geometric distribution as discrete exponential distribution
            avg_vms = 1.0 * (self.max_vms_per_host * self.num_hosts) / self.num_tenants
            vm_counts = stats.geom.rvs(size=self.num_tenants, loc=self.min_vms, p=(1.0 / avg_vms))

            for t in range(self.num_tenants):
                self.tenants_maps[t]['vm_count'] = int(vm_counts[t])
                self.tenants['vm_count'] += int(vm_counts[t])
        elif self.vm_dist == 'expon-mean':
            avg_vms = 1.0 * (self.max_vms_per_host * self.num_hosts) / self.num_tenants
            vm_counts = np.int64(np.floor(stats.expon.rvs(size=self.num_tenants, loc=self.min_vms, scale=avg_vms)))

            for t in range(self.num_tenants):
                self.tenants_maps[t]['vm_count'] = int(vm_counts[t])
                self.tenants['vm_count'] += int(vm_counts[t])
        elif self.vm_dist == 'expon':
            vm_counts = np.int64(np.floor((((stats.expon.rvs(size=self.num_tenants, scale=(1.0 / 4)) / 10) *
                                            (self.max_vms - self.min_vms)) % (
                                           self.max_vms - self.min_vms)) + self.min_vms))

            for t in range(self.num_tenants):
                self.tenants_maps[t]['vm_count'] = int(vm_counts[t])
                self.tenants['vm_count'] += int(vm_counts[t])
        else:
            raise (Exception("invalid dist parameter for vm allocation"))

    def _get_tenant_to_group_count_map(self):
        # ... weighted assignment of groups (based on VMs) to tenants
        for t in range(self.num_tenants):
            group_count = np.int64(np.floor(self.tenants_maps[t]['vm_count'] /
                                            self.tenants['vm_count'] * self.num_groups))
            self.tenants_maps[t]['group_count'] = int(group_count)
            self.tenants['group_count'] += int(group_count)

    def _get_tenant_groups_to_sizes_map(self):
        if self.group_size_dist == 'uniform':
            for t in range(self.num_tenants):
                sizes = stats.randint.rvs(low=self.min_group_size, high=self.tenants_maps[t]['vm_count'],
                                          size=self.tenants_maps[t]['group_count'])

                for g, size in enumerate(sizes):
                    self.tenants_maps[t]['groups_map'][g]['size'] = int(size)
        else:
            raise (Exception("invalid dist parameter for group size allocation"))

    def _get_tenant_groups_to_vms_map(self):
        for t in range(self.num_tenants):
            for g in range(self.tenants_maps[t]['group_count']):
                self.tenants_maps[t]['groups_map'][g]['vms'] = np.random.choice(
                    a=self.tenants_maps[t]['vm_count'],
                    size=self.tenants_maps[t]['groups_map'][g]['size'], replace=False)


if __name__ == "__main__":
    data = dict()

    o_tenants = Tenants(data=data, max_vms_per_host=20, num_tenants=100, min_vms=10, max_vms=100, vm_dist='expon',
                        num_groups=1000, min_group_size=5, group_size_dist='uniform')
