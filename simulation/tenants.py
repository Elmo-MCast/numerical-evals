import pandas as pd
import numpy as np
import multiprocessing
from simulation.utils import bar_range


def unwrap_tenant_groups_to_vms_map(arg, **kwarg):
    return Tenants._get_tenant_groups_to_vms_map(*arg, **kwarg)


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
                                'maps': {
                                    'vm_counts': None,
                                    'group_counts': None,
                                    'groups': [None] * self.num_tenants}}

        self.tenants = self.data['tenants']
        self.tenants_maps = self.tenants['maps']

        self._get_tenant_to_vm_count_map()

        if debug:
            print(pd.Series(self.tenants_maps['vm_counts']).describe())
            print("VM Count: %s" % self.tenants['vm_count'])

        self._get_tenant_to_group_count_map()

        if debug:
            print(pd.Series(self.tenants_maps['group_counts']).describe())
            print("Sum: %s" % self.tenants['group_count'])

        for t in range(self.num_tenants):
            self.tenants_maps['groups'][t] = {'sizes': None, 'vms': None}

        self._get_tenant_groups_to_sizes_map()

        if debug:
            _groups = self.tenants_maps['groups']
            _group_sizes_for_all_tenants = []
            for t in range(self.num_tenants):
                _group_sizes_for_all_tenants += list(_groups[t]['sizes'])
            print(pd.Series(_group_sizes_for_all_tenants).describe())

        # self._get_tenant_groups_to_vms_map()
        self._run_tenant_groups_to_vms_map()

    def _get_tenant_to_vm_count_map(self):
        if self.vm_dist == 'expon':
            vm_counts = np.empty(shape=self.num_tenants, dtype=int)
            samples = np.random.random(size=self.num_tenants)
            outliers = np.where(samples < 0.02)
            vm_counts[outliers] = np.random.randint(low=self.min_vms, high=self.max_vms + 1, size=len(outliers[0]))
            non_outliers = np.where(samples >= 0.02)
            vm_counts[non_outliers] = (((np.random.exponential(scale=1/4, size=len(non_outliers[0])) / 10)
                                       * (self.max_vms - self.min_vms)).astype(int)
                                       % (self.max_vms - self.min_vms) + self.min_vms)
            self.tenants['vm_count'] = sum(vm_counts)
            self.tenants_maps['vm_counts'] = vm_counts
        else:
            raise (Exception("invalid dist parameter for vm allocation"))

    def _get_tenant_to_group_count_map(self):
        # ... weighted assignment of groups (based on VMs) to tenants
        vm_count = self.tenants['vm_count']
        group_counts = (self.tenants_maps['vm_counts'] / vm_count * self.num_groups).astype(int)

        self.tenants['group_count'] = sum(group_counts)
        self.tenants_maps['group_counts'] = group_counts

    def _get_tenant_groups_to_sizes_map(self):
        if self.group_size_dist == 'uniform':
            vm_counts = self.tenants_maps['vm_counts']
            group_counts = self.tenants_maps['group_counts']
            groups = self.tenants_maps['groups']
            for t in bar_range(self.num_tenants, desc='tenants:group sizes'):
                vm_count = vm_counts[t]
                group_count = group_counts[t]
                groups[t]['sizes'] = np.random.randint(low=self.min_group_size, high=vm_count + 1, size=group_count)
        elif self.group_size_dist == 'wve':  # ... using mix3 distribution from the dcn-mcast paper.
            vm_counts = self.tenants_maps['vm_counts']
            group_counts = self.tenants_maps['group_counts']
            groups = self.tenants_maps['groups']
            for t in bar_range(self.num_tenants, desc='tenants:group sizes'):
                vm_count = vm_counts[t]
                group_count = group_counts[t]
                sizes = np.empty(shape=group_count, dtype=int)
                samples = np.random.random(size=group_count)
                outliers = np.where(samples < 0.02)
                sizes[outliers] = (vm_count - (np.random.gamma(shape=2, scale=0.1, size=len(outliers[0])) *
                                               vm_count / 15).astype(int) % vm_count)
                non_outliers = np.where(samples >= 0.02)
                sizes[non_outliers] = (np.random.gamma(shape=2, scale=0.2, size=len(non_outliers[0])) * vm_count / 15 +
                                       self.min_group_size - 1).astype(int) % vm_count + 1
                indexes = np.where(sizes < self.min_group_size)
                sizes[indexes] = self.min_group_size
                groups[t]['sizes'] = sizes
        else:
            raise (Exception("invalid dist parameter for group size allocation"))

    # def _get_tenant_groups_to_vms_map(self):
    #     for t in bar_range(self.num_tenants, desc='tenants:groups->vms'):
    #         vm_count = self.tenants['vm_counts'][t]
    #         group_count = self.tenants['group_counts'][t]
    #         group = self.tenants['groups'][t]
    #         group['vms'] = [None] * group_count
    #         for g in range(group_count):
    #             group['vms'][g] = np.random.choice(vm_count, group['sizes'][g], replace=False)

    @staticmethod
    def _get_tenant_groups_to_vms_map(vm_counts, group_counts, groups, num_tenants):
        groups_vms = [None] * num_tenants
        for t in bar_range(num_tenants, desc='tenants:groups->vms'):
            vm_count = vm_counts[t]
            group_count = group_counts[t]
            group = groups[t]
            group_sizes = group['sizes']
            group_vms = [None] * group_count
            for g in range(group_count):
                group_vms[g] = np.random.choice(vm_count, group_sizes[g], replace=False)
            groups_vms[t] = group_vms
        return groups_vms

    def _run_tenant_groups_to_vms_map(self):
        num_jobs = 4
        if (self.num_tenants % num_jobs) != 0:
            raise(Exception('input not divisible by num_jobs'))

        input_size = int(self.num_tenants / num_jobs)
        input_groups = [(i, i + input_size) for i in range(0, self.num_tenants, input_size)]
        inputs = [(self.tenants_maps['vm_counts'][i:j],
                   self.tenants_maps['group_counts'][i:j],
                   self.tenants_maps['groups'][i:j],
                   input_size) for i, j in input_groups]

        pool = multiprocessing.Pool()
        results = pool.map(unwrap_tenant_groups_to_vms_map, [i for i in inputs])

        groups = self.tenants_maps['groups']
        for i in range(len(results)):
            result = results[i]
            t_low, t_high = input_groups[i]
            for j, t in enumerate(range(t_low, t_high)):
                groups[t]['vms'] = result[j]
