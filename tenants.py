from threading import Thread
import operator
from functools import reduce
import pandas as pd
import numpy as np
from scipy import stats


class Tenants:
    def __init__(self,
                 num_hosts=1056 * 48, max_vms_per_host=20,
                 num_tenants=3000, min_vms=10, max_vms=5000, vm_dist='expon',
                 num_groups=100000, min_group_size=5, group_size_dist='uniform',
                 multi_threaded=True, num_threads=2):
        self.num_tenants = num_tenants
        self.num_hosts = num_hosts
        self.max_vms_per_host = max_vms_per_host
        self.min_vms = min_vms
        self.max_vms = max_vms
        self.vm_dist = vm_dist
        self.num_groups = num_groups
        self.min_group_size = min_group_size
        self.group_size_dist = group_size_dist
        self.multi_threaded = multi_threaded
        self.num_threads = num_threads

        if self.multi_threaded:
            self.num_chunks = self.num_threads
            if self.num_tenants % self.num_chunks != 0:
                raise Exception("number of threads should be a multiple of tenants count")
            self.chunk_size = int(self.num_tenants / self.num_chunks)

        self.tenant_vm_count_map = None
        self._get_tenant_vm_count_map()

        self.tenant_group_count_map = None
        self._get_tenant_group_count_map()

        self.tenant_groups_sizes_map = None
        self._get_groups_sizes_map()

        self.tenant_groups_to_vms_map = None
        self._get_tenant_groups_to_vms_map()

        print('tenants: initialized.')

    def _get_tenant_vm_count_map(self):
        if self.vm_dist == 'geom':  # ... using geometric distribution as discrete exponential distribution
            avg_vms = 1.0 * (self.max_vms_per_host * self.num_hosts) / self.num_tenants
            self.tenant_vm_count_map = pd.Series(
                stats.geom.rvs(size=self.num_tenants, loc=self.min_vms, p=(1.0 / avg_vms)))
        elif self.vm_dist == 'expon-mean':
            avg_vms = 1.0 * (self.max_vms_per_host * self.num_hosts) / self.num_tenants
            self.tenant_vm_count_map = pd.Series(np.int64(np.floor(
                stats.expon.rvs(size=self.num_tenants, loc=self.min_vms, scale=avg_vms))))
        elif self.vm_dist == 'expon':
            self.tenant_vm_count_map = pd.Series(np.int64(np.floor(
                (((stats.expon.rvs(size=self.num_tenants, scale=(1.0 / 2)) / 10) * (self.max_vms - self.min_vms))
                 % (self.max_vms - self.min_vms)) + self.min_vms)))
        else:
            raise (Exception("invalid dist parameter for vm allocation"))

    def _get_tenant_group_count_map(self):
        # ... weighted assignment of groups (based on VMs) to tenants
        self.tenant_group_count_map = pd.Series(
            np.int64(np.floor((self.tenant_vm_count_map / self.tenant_vm_count_map.sum()) * self.num_groups)))

    def _get_groups_sizes_map_chunk(self, groups_sizes_map_chunks, chunk_id, chunk_size):
        base_index = chunk_id * chunk_size
        groups_sizes_map = [None] * chunk_size

        for t in range(base_index, base_index + chunk_size):
            groups_sizes_map[t % chunk_size] = pd.Series(stats.randint.rvs(low=self.min_group_size,
                                                                           high=self.tenant_vm_count_map[t],
                                                                           size=self.tenant_group_count_map[t]))
        groups_sizes_map_chunks[chunk_id] = groups_sizes_map

    def _get_groups_sizes_map(self):
        if self.group_size_dist == 'uniform':
            if not self.multi_threaded:
                self.tenant_groups_sizes_map = [None] * self.num_tenants

                for t in range(self.num_tenants):
                    self.tenant_groups_sizes_map[t] = pd.Series(stats.randint.rvs(low=self.min_group_size,
                                                                                  high=self.tenant_vm_count_map[t],
                                                                                  size=self.tenant_group_count_map[t]))
            else:
                groups_sizes_map_chunks = [None] * self.num_chunks
                groups_sizes_map_threads = [None] * self.num_chunks

                for i in range(self.num_chunks):
                    groups_sizes_map_threads[i] = Thread(target=self._get_groups_sizes_map_chunk,
                                                         args=(groups_sizes_map_chunks, i, self.chunk_size))
                    groups_sizes_map_threads[i].start()

                for i in range(self.num_chunks):
                    groups_sizes_map_threads[i].join()

                self.tenant_groups_sizes_map = reduce(operator.concat, groups_sizes_map_chunks)
        else:
            raise (Exception("invalid dist parameter for group size allocation"))

    def _get_tenant_groups_to_vms_map_chunk(self, tenant_groups_to_vms_map_chunks, chunk_id, chunk_size):
        base_index = chunk_id * chunk_size
        tenant_groups_to_vms_map = [None] * chunk_size

        for t in range(base_index, base_index + chunk_size):
            _groups_to_vms_map = [None] * self.tenant_group_count_map[t]

            for g in range(self.tenant_group_count_map[t]):
                _groups_to_vms_map[g] = pd.Series(stats.randint.rvs(low=0,
                                                                    high=self.tenant_vm_count_map[t],
                                                                    size=self.tenant_groups_sizes_map[t][g]))
            tenant_groups_to_vms_map[t % chunk_size] = _groups_to_vms_map

        tenant_groups_to_vms_map_chunks[chunk_id] = tenant_groups_to_vms_map

    def _get_tenant_groups_to_vms_map(self):
        if not self.multi_threaded:
            self.tenant_groups_to_vms_map = [None] * self.num_tenants

            for t in range(self.num_tenants):
                _groups_to_vms_map = [None] * self.tenant_group_count_map[t]

                for g in range(self.tenant_group_count_map[t]):
                    _groups_to_vms_map[g] = pd.Series(stats.randint.rvs(low=0,
                                                                        high=self.tenant_vm_count_map[t],
                                                                        size=self.tenant_groups_sizes_map[t][g]))
                self.tenant_groups_to_vms_map[t] = _groups_to_vms_map
        else:
            tenant_groups_to_vms_map_chunks = [None] * self.num_chunks
            tenant_groups_to_vms_map_threads = [None] * self.num_chunks

            for i in range(self.num_chunks):
                tenant_groups_to_vms_map_threads[i] = Thread(target=self._get_tenant_groups_to_vms_map_chunk,
                                                             args=(tenant_groups_to_vms_map_chunks, i, self.chunk_size))
                tenant_groups_to_vms_map_threads[i].start()

            for i in range(self.num_chunks):
                tenant_groups_to_vms_map_threads[i].join()

            self.tenant_groups_to_vms_map = reduce(operator.concat, tenant_groups_to_vms_map_chunks)
