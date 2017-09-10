from multiprocessing import Pool
import operator
from functools import reduce
import pandas as pd
import numpy as np
from scipy import stats


def _get_tenant_vm_count_map(vm_dist, max_vms_per_host, num_hosts, num_tenants,
                             min_vms, max_vms):
    if vm_dist == 'geom':
        avg_vms = 1.0 * (max_vms_per_host * num_hosts) / num_tenants
        return pd.Series(stats.geom.rvs(size=num_tenants, loc=min_vms, p=(1.0 / avg_vms)))
    elif vm_dist == 'expon-mean':
        avg_vms = 1.0 * (max_vms_per_host * num_hosts) / num_tenants
        return pd.Series(np.int64(np.floor(stats.expon.rvs(size=num_tenants, loc=min_vms, scale=avg_vms))))
    elif vm_dist == 'expon':
        return pd.Series(np.int64(np.floor((((stats.expon.rvs(size=num_tenants, scale=(1.0 / 2)) / 10) *
                                             (max_vms - min_vms)) % (max_vms - min_vms)) + min_vms)))
    else:
        raise (Exception("invalid dist parameter for vm allocation"))


def _get_tenant_group_count_map(tenant_vm_count_map, num_groups):
    # ... weighted assignment of groups (based on VMs) to tenants
    return pd.Series(np.int64(np.floor((tenant_vm_count_map / tenant_vm_count_map.sum()) * num_groups)))


def _get_tenant_groups_sizes_map_chunk(min_group_size, tenant_vm_count_map, tenant_group_count_map,
                                       chunk_id, chunk_size):
    base_index = chunk_id * chunk_size
    _groups_sizes_map = [None] * chunk_size

    for t in range(base_index, base_index + chunk_size):
        _groups_sizes_map[t % chunk_size] = pd.Series(stats.randint.rvs(low=min_group_size,
                                                                        high=tenant_vm_count_map[t],
                                                                        size=tenant_group_count_map[t]))
    return _groups_sizes_map


def _get_tenant_groups_sizes_map(group_size_dist, multi_threaded, num_tenants, min_group_size,
                                 tenant_vm_count_map, tenant_group_count_map, num_chunks, chunk_size):
    if group_size_dist == 'uniform':
        if not multi_threaded:
            _tenant_groups_sizes_map = [None] * num_tenants

            for t in range(num_tenants):
                _tenant_groups_sizes_map[t] = pd.Series(stats.randint.rvs(low=min_group_size,
                                                                          high=tenant_vm_count_map[t],
                                                                          size=tenant_group_count_map[t]))
        else:
            tenant_groups_sizes_map_pool = Pool(processes=num_chunks)

            tenant_groups_sizes_map_results = tenant_groups_sizes_map_pool.starmap(
                _get_tenant_groups_sizes_map_chunk,
                [(min_group_size, tenant_vm_count_map, tenant_group_count_map, i, chunk_size) for i in
                 range(num_chunks)])

            _tenant_groups_sizes_map = reduce(operator.concat, tenant_groups_sizes_map_results)

        return _tenant_groups_sizes_map
    else:
        raise (Exception("invalid dist parameter for group size allocation"))


def _get_tenant_groups_to_vms_map_chunk(tenant_group_count_map, tenant_vm_count_map, tenant_groups_sizes_map,
                                        chunk_id, chunk_size):
    base_index = chunk_id * chunk_size
    _tenant_groups_to_vms_map = [None] * chunk_size

    for t in range(base_index, base_index + chunk_size):
        _groups_to_vms_map = [None] * tenant_group_count_map[t]

        for g in range(tenant_group_count_map[t]):
            _groups_to_vms_map[g] = pd.Series(stats.randint.rvs(low=0,
                                                                high=tenant_vm_count_map[t],
                                                                size=tenant_groups_sizes_map[t][g]))
        _tenant_groups_to_vms_map[t % chunk_size] = _groups_to_vms_map

    return _tenant_groups_to_vms_map


def _get_tenant_groups_to_vms_map(multi_threaded, num_tenants, tenant_group_count_map, tenant_vm_count_map,
                                  tenant_groups_sizes_map, num_chunks, chunk_size):
    if not multi_threaded:
        _tenant_groups_to_vms_map = [None] * num_tenants

        for t in range(num_tenants):
            _groups_to_vms_map = [None] * tenant_group_count_map[t]

            for g in range(tenant_group_count_map[t]):
                _groups_to_vms_map[g] = pd.Series(stats.randint.rvs(low=0,
                                                                    high=tenant_vm_count_map[t],
                                                                    size=tenant_groups_sizes_map[t][g]))
            _tenant_groups_to_vms_map[t] = _groups_to_vms_map
    else:
        tenant_groups_to_vms_map_pool = Pool(processes=num_chunks)

        tenant_groups_to_vms_map_results = tenant_groups_to_vms_map_pool.starmap(
            _get_tenant_groups_to_vms_map_chunk,
            [(tenant_group_count_map, tenant_vm_count_map, tenant_groups_sizes_map, i, chunk_size)
             for i in range(num_chunks)])

        _tenant_groups_to_vms_map = reduce(operator.concat, tenant_groups_to_vms_map_results)

    return _tenant_groups_to_vms_map


def initialize(num_hosts=1056 * 48, max_vms_per_host=20,
               num_tenants=3000, min_vms=10, max_vms=5000, vm_dist='expon',
               num_groups=100000, min_group_size=5, group_size_dist='uniform',
               multi_threaded=True, num_threads=2):
    if multi_threaded:
        num_chunks = num_threads
        if num_tenants % num_chunks != 0:
            raise Exception("number of threads should be a multiple of tenants count")
        chunk_size = int(num_tenants / num_chunks)

        # print('tenants: no. of chunks %s' % self.num_chunks)
    else:
        num_chunks = 0
        chunk_size = 0

    _tenant_vm_count_map = _get_tenant_vm_count_map(vm_dist, max_vms_per_host, num_hosts, num_tenants,
                                                    min_vms, max_vms)

    _tenant_group_count_map = _get_tenant_group_count_map(_tenant_vm_count_map, num_groups)

    _tenant_groups_sizes_map = _get_tenant_groups_sizes_map(group_size_dist, multi_threaded, num_tenants,
                                                            min_group_size, _tenant_vm_count_map,
                                                            _tenant_group_count_map, num_chunks, chunk_size)

    _tenant_groups_to_vms_map = _get_tenant_groups_to_vms_map(multi_threaded, num_tenants, _tenant_group_count_map,
                                                              _tenant_vm_count_map, _tenant_groups_sizes_map,
                                                              num_chunks, chunk_size)

    print('tenants: initialized.')

    return {'tenant_vm_count_map': _tenant_vm_count_map,
            'tenant_group_count_map': _tenant_group_count_map,
            'tenant_groups_sizes_map': _tenant_groups_sizes_map,
            'tenant_groups_to_vms_map': _tenant_groups_to_vms_map,
            'num_tenants': num_tenants,
            'max_vms_per_host': max_vms_per_host}


if __name__ == "__main__":
    o_tenants = initialize(num_hosts=48 * 48, max_vms_per_host=20,
                           num_tenants=128, min_vms=10, max_vms=100, vm_dist='expon',
                           num_groups=1000, min_group_size=5, group_size_dist='uniform',
                           multi_threaded=True, num_threads=8)
