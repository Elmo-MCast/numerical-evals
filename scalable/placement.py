from multiprocessing import Pool
import operator
from functools import reduce
import pandas as pd
import numpy as np
from bitstring import BitArray


def _get_tenant_vms_to_host_map(dist, network, tenants):
    if dist == 'uniform':
        _tenant_vms_to_host_map = [None] * tenants['num_tenants']
        available_hosts = [h for h in range(network['num_hosts'])]
        selected_hosts_count = [0] * network['num_hosts']

        for t in range(tenants['num_tenants']):
            _tenant_vms_to_host_map[t] = pd.Series(
                np.random.choice(a=available_hosts,
                                 size=tenants['tenant_vm_count_map'][t], replace=False))

            for _, host in _tenant_vms_to_host_map[t].iteritems():
                selected_hosts_count[host] += 1

            max_host_count = max(selected_hosts_count)
            if max_host_count == tenants['max_vms_per_host']:
                removed_hosts = [h for h, host_count in enumerate(selected_hosts_count)
                                 if host_count == max_host_count]
                available_hosts = list(set(available_hosts) - set(removed_hosts))
                for removed_host in sorted(removed_hosts, reverse=True):
                    selected_hosts_count[removed_host] = -1

        return _tenant_vms_to_host_map
    elif dist == 'colocate':
        _tenant_vms_to_host_map = [None] * tenants['num_tenants']
        available_leafs = [l for l in range(network['num_leafs'])]

        available_hosts_per_leaf = [None] * network['num_leafs']
        selected_hosts_count_per_leaf = [None] * network['num_leafs']
        for l in range(network['num_leafs']):
            available_hosts_per_leaf[l] = [(l * network['num_hosts_per_leaf']) + h
                                           for h in range(network['num_hosts_per_leaf'])]
            selected_hosts_count_per_leaf[l] = [0] * network['num_hosts_per_leaf']

        for t in range(tenants['num_tenants']):
            _tenant_vms_to_host_map[t] = pd.Series([None] * tenants['tenant_vm_count_map'][t])

            running_index = 0
            running_count = tenants['tenant_vm_count_map'][t]
            while running_count > 0:
                selected_leaf = np.random.choice(a=available_leafs, size=1)[0]
                selected_leaf_hosts_count = len(available_hosts_per_leaf[selected_leaf])

                if int(running_count / selected_leaf_hosts_count) > 0:
                    for h in range(selected_leaf_hosts_count):
                        _tenant_vms_to_host_map[t][running_index] = available_hosts_per_leaf[selected_leaf][h]
                        selected_hosts_count_per_leaf[selected_leaf][h] += 1
                        running_index += 1
                    running_count -= selected_leaf_hosts_count
                else:
                    for h in range(running_count):
                        _tenant_vms_to_host_map[t][running_index] = available_hosts_per_leaf[selected_leaf][h]
                        selected_hosts_count_per_leaf[selected_leaf][h] += 1
                        running_index += 1
                    running_count = 0

                max_host_count = max(selected_hosts_count_per_leaf[selected_leaf])
                if max_host_count == tenants['max_vms_per_host']:
                    removed_hosts = [h for h, host_count in enumerate(selected_hosts_count_per_leaf[selected_leaf])
                                     if host_count == max_host_count]
                    for removed_host in sorted(removed_hosts, reverse=True):
                        del available_hosts_per_leaf[selected_leaf][removed_host]
                        del selected_hosts_count_per_leaf[selected_leaf][removed_host]

                    if len(available_hosts_per_leaf[selected_leaf]) == 0:
                        available_leafs.remove(selected_leaf)

        return _tenant_vms_to_host_map
    else:
        raise (Exception("invalid dist parameter for vm to host allocation"))


def _get_tenant_vms_to_leaf_map_chunk(network, tenant_vms_to_host_map, chunk_id, chunk_size):
    base_index = chunk_id * chunk_size
    _tenant_vms_to_leaf_map = [None] * chunk_size

    for t in range(base_index, base_index + chunk_size):
        _tenant_vms_to_leaf_map[t % chunk_size] = pd.Series(
            [network['host_to_leaf_map'][host] for _, host in tenant_vms_to_host_map[t].iteritems()])

    return _tenant_vms_to_leaf_map


def _get_tenant_vms_to_leaf_map(multi_threaded, network, tenants, tenant_vms_to_host_map,
                                num_chunks, chunk_size):
    if not multi_threaded:
        _tenant_vms_to_leaf_map = [None] * tenants['num_tenants']

        for t in range(tenants['num_tenants']):
            _tenant_vms_to_leaf_map[t] = pd.Series([network['host_to_leaf_map'][host]
                                                    for _, host in tenant_vms_to_host_map[t].iteritems()])
    else:
        tenant_vms_to_leaf_map_pool = Pool(processes=num_chunks)

        tenant_vms_to_leaf_map_results = tenant_vms_to_leaf_map_pool.starmap(
            _get_tenant_vms_to_leaf_map_chunk,
            [(network, tenant_vms_to_host_map, i, chunk_size)
             for i in range(num_chunks)])

        _tenant_vms_to_leaf_map = reduce(operator.concat, tenant_vms_to_leaf_map_results)

    return _tenant_vms_to_leaf_map


def _get_tenant_groups_to_leafs_map_chunk(tenants, tenant_vms_to_leaf_map, chunk_id, chunk_size):
    base_index = chunk_id * chunk_size
    _tenant_groups_to_leafs_map = [None] * chunk_size

    for t in range(base_index, base_index + chunk_size):
        _groups_to_leaf_map = [None] * tenants['tenant_group_count_map'][t]

        for g in range(tenants['tenant_group_count_map'][t]):
            _groups_to_leaf_map[g] = pd.Series(list(
                {tenant_vms_to_leaf_map[t][vm]
                 for _, vm in tenants['tenant_groups_to_vms_map'][t][g].iteritems()}))
        _tenant_groups_to_leafs_map[t % chunk_size] = _groups_to_leaf_map

    return _tenant_groups_to_leafs_map


def _get_tenant_groups_to_leafs_map(multi_threaded, tenants, tenant_vms_to_leaf_map,
                                    num_chunks, chunk_size):
    if not multi_threaded:
        tenant_groups_to_leafs_map = [None] * tenants['num_tenants']

        for t in range(tenants['num_tenants']):
            _groups_to_leaf_map = [None] * tenants['tenant_group_count_map'][t]

            for g in range(tenants['tenant_group_count_map'][t]):
                _groups_to_leaf_map[g] = pd.Series(list(
                    {tenant_vms_to_leaf_map[t][vm]
                     for _, vm in tenants['tenant_groups_to_vms_map'][t][g].iteritems()}))
            tenant_groups_to_leafs_map[t] = _groups_to_leaf_map
    else:
        tenant_groups_to_leafs_map_pool = Pool(processes=num_chunks)

        tenant_groups_to_leafs_map_results = tenant_groups_to_leafs_map_pool.starmap(
            _get_tenant_groups_to_leafs_map_chunk,
            [(tenants, tenant_vms_to_leaf_map, i, chunk_size)
             for i in range(num_chunks)])

        tenant_groups_to_leafs_map = reduce(operator.concat, tenant_groups_to_leafs_map_results)

    return tenant_groups_to_leafs_map


def _get_tenant_groups_to_leaf_count_chunk(tenants, tenant_groups_to_leafs_map, chunk_id, chunk_size):
    base_index = chunk_id * chunk_size
    _tenant_groups_to_leaf_count = [None] * chunk_size

    for t in range(base_index, base_index + chunk_size):
        _groups_to_leaf_count = [None] * tenants['tenant_group_count_map'][t]

        for g in range(tenants['tenant_group_count_map'][t]):
            _groups_to_leaf_count[g] = len(tenant_groups_to_leafs_map[t][g])

        _tenant_groups_to_leaf_count[t % chunk_size] = pd.Series(_groups_to_leaf_count)

    return _tenant_groups_to_leaf_count


def _get_tenant_groups_to_leaf_count(multi_threaded, tenants, tenant_groups_to_leafs_map,
                                     num_chunks, chunk_size):
    if not multi_threaded:
        _tenant_groups_to_leaf_count = [None] * tenants['num_tenants']

        for t in range(tenants['num_tenants']):
            _groups_to_leaf_count = [None] * tenants['tenant_group_count_map'][t]

            for g in range(tenants['tenant_group_count_map'][t]):
                _groups_to_leaf_count[g] = len(tenant_groups_to_leafs_map[t][g])

            _tenant_groups_to_leaf_count[t] = pd.Series(_groups_to_leaf_count)
    else:
        tenant_groups_to_leaf_count_pool = Pool(processes=num_chunks)

        tenant_groups_to_leaf_count_results = tenant_groups_to_leaf_count_pool.starmap(
            _get_tenant_groups_to_leaf_count_chunk,
            [(tenants, tenant_groups_to_leafs_map, i, chunk_size)
             for i in range(num_chunks)])

        _tenant_groups_to_leaf_count = reduce(operator.concat, tenant_groups_to_leaf_count_results)

    return _tenant_groups_to_leaf_count


def _get_tenant_groups_leafs_to_hosts_map_chunk(tenants, tenant_groups_to_leaf_count, num_bitmaps,
                                                tenant_vms_to_leaf_map, tenant_vms_to_host_map,
                                                chunk_id, chunk_size):
    base_index = chunk_id * chunk_size
    _tenant_groups_leafs_to_hosts_map = [None] * chunk_size

    for t in range(base_index, base_index + chunk_size):
        _groups_leafs_to_hosts_map = [None] * tenants['tenant_group_count_map'][t]

        for g in range(tenants['tenant_group_count_map'][t]):
            _leafs_to_hosts_dict = dict()

            if tenant_groups_to_leaf_count[t][g] > num_bitmaps:
                for _, vm in tenants['tenant_groups_to_vms_map'][t][g].iteritems():
                    if tenant_vms_to_leaf_map[t][vm] in _leafs_to_hosts_dict:
                        _leafs_to_hosts_dict[tenant_vms_to_leaf_map[t][vm]] |= {tenant_vms_to_host_map[t][vm]}
                    else:
                        _leafs_to_hosts_dict[tenant_vms_to_leaf_map[t][vm]] = {tenant_vms_to_host_map[t][vm]}

            _groups_leafs_to_hosts_map[g] = _leafs_to_hosts_dict

        _tenant_groups_leafs_to_hosts_map[t % chunk_size] = _groups_leafs_to_hosts_map

    return _tenant_groups_leafs_to_hosts_map


def _get_tenant_groups_leafs_to_hosts_map(multi_threaded, tenants, tenant_groups_to_leaf_count, num_bitmaps,
                                          tenant_vms_to_leaf_map, tenant_vms_to_host_map, num_chunks, chunk_size):
    if not multi_threaded:
        _tenant_groups_leafs_to_hosts_map = [None] * tenants['num_tenants']

        for t in range(tenants['num_tenants']):
            _groups_leafs_to_hosts_map = [None] * tenants['tenant_group_count_map'][t]

            for g in range(tenants['tenant_group_count_map'][t]):
                _leafs_to_hosts_dict = dict()

                if tenant_groups_to_leaf_count[t][g] > num_bitmaps:
                    for _, vm in tenants['tenant_groups_to_vms_map'][t][g].iteritems():
                        if tenant_vms_to_leaf_map[t][vm] in _leafs_to_hosts_dict:
                            _leafs_to_hosts_dict[tenant_vms_to_leaf_map[t][vm]] |= {tenant_vms_to_host_map[t][vm]}
                        else:
                            _leafs_to_hosts_dict[tenant_vms_to_leaf_map[t][vm]] = {tenant_vms_to_host_map[t][vm]}

                _groups_leafs_to_hosts_map[g] = _leafs_to_hosts_dict

            _tenant_groups_leafs_to_hosts_map[t] = _groups_leafs_to_hosts_map
    else:
        tenant_groups_leafs_to_hosts_map_pool = Pool(processes=num_chunks)

        tenant_groups_leafs_to_hosts_map_results = tenant_groups_leafs_to_hosts_map_pool.starmap(
            _get_tenant_groups_leafs_to_hosts_map_chunk,
            [(tenants, tenant_groups_to_leaf_count, num_bitmaps, tenant_vms_to_leaf_map, tenant_vms_to_host_map,
              i, chunk_size) for i in range(num_chunks)])

        _tenant_groups_leafs_to_hosts_map = reduce(operator.concat, tenant_groups_leafs_to_hosts_map_results)

    return _tenant_groups_leafs_to_hosts_map


def _get_tenant_groups_leafs_to_bitmap_map_chunk(network, tenants, tenant_groups_to_leaf_count, num_bitmaps,
                                                 tenant_groups_leafs_to_hosts_map, chunk_id, chunk_size):
    base_index = chunk_id * chunk_size
    _tenant_groups_leafs_to_bitmap_map = [None] * chunk_size

    for t in range(base_index, base_index + chunk_size):
        _groups_leafs_to_bitmap_map = [None] * tenants['tenant_group_count_map'][t]

        for g in range(tenants['tenant_group_count_map'][t]):
            _leafs_to_bitmap_dict = dict()

            if tenant_groups_to_leaf_count[t][g] > num_bitmaps:
                for l in tenant_groups_leafs_to_hosts_map[t][g]:
                    _leafs_to_bitmap_dict[l] = dict()

                    _leafs_to_bitmap_dict[l]['actual'] = BitArray(network['num_hosts_per_leaf'])
                    for h in tenant_groups_leafs_to_hosts_map[t][g][l]:
                        _leafs_to_bitmap_dict[l]['actual'][h % network['num_hosts_per_leaf']] = 1

                    _leafs_to_bitmap_dict[l]['sorted'] = BitArray(
                        sorted(_leafs_to_bitmap_dict[l]['actual'], reverse=True))

            _groups_leafs_to_bitmap_map[g] = _leafs_to_bitmap_dict

        _tenant_groups_leafs_to_bitmap_map[t % chunk_size] = _groups_leafs_to_bitmap_map

    return _tenant_groups_leafs_to_bitmap_map


def _get_tenant_groups_leafs_to_bitmap_map(multi_threaded, network, tenants, tenant_groups_to_leaf_count, num_bitmaps,
                                           tenant_groups_leafs_to_hosts_map, num_chunks, chunk_size):
    if not multi_threaded:
        _tenant_groups_leafs_to_bitmap_map = [None] * tenants['num_tenants']

        for t in range(tenants['num_tenants']):
            _groups_leafs_to_bitmap_map = [None] * tenants['tenant_group_count_map'][t]

            for g in range(tenants['tenant_group_count_map'][t]):
                _leafs_to_bitmap_dict = dict()

                if tenant_groups_to_leaf_count[t][g] > num_bitmaps:
                    for l in tenant_groups_leafs_to_hosts_map[t][g]:
                        _leafs_to_bitmap_dict[l] = dict()

                        _leafs_to_bitmap_dict[l]['actual'] = BitArray(network['num_hosts_per_leaf'])
                        for h in tenant_groups_leafs_to_hosts_map[t][g][l]:
                            _leafs_to_bitmap_dict[l]['actual'][h % network['num_hosts_per_leaf']] = 1

                        _leafs_to_bitmap_dict[l]['sorted'] = BitArray(
                            sorted(_leafs_to_bitmap_dict[l]['actual'], reverse=True))

                _groups_leafs_to_bitmap_map[g] = _leafs_to_bitmap_dict

            _tenant_groups_leafs_to_bitmap_map[t] = _groups_leafs_to_bitmap_map
    else:
        tenant_groups_leafs_to_bitmap_map_pool = Pool(processes=num_chunks)

        tenant_groups_leafs_to_bitmap_map_result = tenant_groups_leafs_to_bitmap_map_pool.starmap(
            _get_tenant_groups_leafs_to_bitmap_map_chunk,
            [(network, tenants, tenant_groups_to_leaf_count, num_bitmaps, tenant_groups_leafs_to_hosts_map,
              i, chunk_size) for i in range(num_chunks)])

        _tenant_groups_leafs_to_bitmap_map = reduce(operator.concat, tenant_groups_leafs_to_bitmap_map_result)

    return _tenant_groups_leafs_to_bitmap_map


def initialize(network, tenants, dist='uniform', num_bitmaps=32, generate_bitmaps=False,
               multi_threaded=True, num_threads=2):
    if multi_threaded:
        num_chunks = num_threads
        if tenants['num_tenants'] % num_chunks != 0:
            raise Exception("number of threads should be a multiple of tenants count")
        chunk_size = int(tenants['num_tenants'] / num_chunks)

        print('placement: no. of chunks %s' % num_chunks)
    else:
        num_chunks = 0
        chunk_size = 0

    _tenant_vms_to_host_map = _get_tenant_vms_to_host_map(dist, network, tenants)

    print('placement[tenant_vms_to_host_map]: initialized.')

    _tenant_vms_to_leaf_map = _get_tenant_vms_to_leaf_map(multi_threaded, network, tenants, _tenant_vms_to_host_map,
                                                          num_chunks, chunk_size)

    print('placement[tenant_vms_to_leaf_map]: initialized.')

    _tenant_groups_to_leafs_map = _get_tenant_groups_to_leafs_map(multi_threaded, tenants, _tenant_vms_to_leaf_map,
                                                                  num_chunks, chunk_size)

    print('placement[tenant_groups_to_leafs_map]: initialized.')

    _tenant_groups_to_leaf_count = _get_tenant_groups_to_leaf_count(multi_threaded, tenants,
                                                                    _tenant_groups_to_leafs_map, num_chunks, chunk_size)

    print('placement[tenant_groups_to_leaf_count]: initialized.')

    if generate_bitmaps:
        _tenant_groups_leafs_to_hosts_map = _get_tenant_groups_leafs_to_hosts_map(multi_threaded, tenants,
                                                                                  _tenant_groups_to_leaf_count,
                                                                                  num_bitmaps,
                                                                                  _tenant_vms_to_leaf_map,
                                                                                  _tenant_vms_to_host_map, num_chunks,
                                                                                  chunk_size)

        print('placement[tenant_groups_leafs_to_hosts_map]: initialized.')

        _tenant_groups_leafs_to_bitmap_map = _get_tenant_groups_leafs_to_bitmap_map(multi_threaded, network, tenants,
                                                                                    _tenant_groups_to_leaf_count,
                                                                                    num_bitmaps,
                                                                                    _tenant_groups_leafs_to_hosts_map,
                                                                                    num_chunks, chunk_size)

        print('placement[tenant_groups_leafs_to_bitmap_map]: initialized.')

    else:
        _tenant_groups_leafs_to_hosts_map = None
        _tenant_groups_leafs_to_bitmap_map = None

    print('placement: initialized.')

    return {'tenant_vms_to_host_map': _tenant_vms_to_host_map,
            'tenant_vms_to_leaf_map': _tenant_vms_to_leaf_map,
            'tenant_groups_to_leafs_map': _tenant_groups_to_leafs_map,
            'tenant_groups_to_leaf_count': _tenant_groups_to_leaf_count,
            'tenant_groups_leafs_to_hosts_map': _tenant_groups_leafs_to_hosts_map,
            'tenant_groups_leafs_to_bitmap_map': _tenant_groups_leafs_to_bitmap_map,
            'num_bitmaps': num_bitmaps}
