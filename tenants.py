import pandas as pd
import numpy as np
from scipy import stats


class Tenants:
    def __init__(self,
                 num_hosts=1056*48, max_vms_per_host=20,
                 num_tenants=3000, min_vms=10, max_vms=5000, vm_dist='expon',
                 num_groups=100000, min_group_size=5, group_size_dist='uniform'):
        self.num_tenants = num_tenants
        self.num_hosts = num_hosts
        self.max_vms_per_host = max_vms_per_host
        self.min_vms = min_vms
        self.max_vms = max_vms
        self.vm_dist = vm_dist
        self.num_groups = num_groups
        self.min_group_size = min_group_size
        self.group_size_dist = group_size_dist

        self.vm_map = None
        self._get_vm_map()

        self.group_map = None
        self._get_group_map()

        self.group_size_map = None
        self._get_group_size_map()

        self.group_to_vm_map = None
        self._get_group_to_vm_map()

    def _get_vm_map(self):
        if self.vm_dist == 'geom':  # ... using geometric distribution as discrete exponential distribution
            avg_vms = 1.0 * (self.max_vms_per_host * self.num_hosts) / self.num_tenants
            self.vm_map = pd.Series(stats.geom.rvs(size=self.num_tenants, loc=self.min_vms, p=(1.0 / avg_vms)))
        elif self.vm_dist == 'expon-mean':
            avg_vms = 1.0 * (self.max_vms_per_host * self.num_hosts) / self.num_tenants
            self.vm_map = pd.Series(np.int64(np.floor(
                stats.expon.rvs(size=self.num_tenants, loc=self.min_vms, scale=avg_vms))))
        elif self.vm_dist == 'expon':
            self.vm_map = pd.Series(np.int64(np.floor(
                (((stats.expon.rvs(size=self.num_tenants, scale=(1.0 / 2)) / 10) * (self.max_vms - self.min_vms))
                 % (self.max_vms - self.min_vms)) + self.min_vms)))
        else:
            raise (Exception("invalid dist parameter for vm allocation"))

    def _get_group_map(self):
        # ... weighted assignment of groups (based on VMs) to tenants
        self.group_map = pd.Series(np.int64(np.floor((self.vm_map / self.vm_map.sum()) * self.num_groups)))

    def _get_group_size_map(self):
        self.group_size_map = [None] * self.num_tenants

        if self.group_size_dist == 'uniform':
            for i in range(self.num_tenants):
                self.group_size_map[i] = pd.Series(stats.randint.rvs(low=self.min_group_size,
                                                                     high=self.vm_map[i],
                                                                     size=self.group_map[i]))
        else:
            raise (Exception("invalid dist parameter for group size allocation"))

    def _get_group_to_vm_map(self):
        self.group_to_vm_map = [None] * self.num_tenants

        for i in range(self.num_tenants):
            _group_to_vm_map = [None] * self.group_map[i]

            for j in range(self.group_map[i]):
                _group_to_vm_map[j] = pd.Series(stats.randint.rvs(low=0,
                                                                  high=self.vm_map[i],
                                                                  size=self.group_size_map[i][j]))
            self.group_to_vm_map[i] = _group_to_vm_map
