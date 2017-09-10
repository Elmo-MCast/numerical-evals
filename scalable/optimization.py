import operator
from functools import reduce
from multiprocessing import Pool
from scalable import algorithms


def _optimize_chunk(tenants, placement, chunk_id, chunk_size):
    base_index = chunk_id * chunk_size
    _tenant_groups_categories_to_bitmap_map = [None] * chunk_size
    _tenant_groups_leafs_to_category_map = [None] * chunk_size
    _tenant_groups_to_redundancy_map = [None] * chunk_size
    _tenant_groups_to_min_bitmap_count = [None] * chunk_size

    for t in range(base_index, base_index + chunk_size):
        _groups_categories_to_bitmap_map = [None] * tenants['tenant_group_count_map'][t]
        _groups_leafs_to_category_map = [None] * tenants['tenant_group_count_map'][t]
        _groups_to_redundancy_map = [None] * tenants['tenant_group_count_map'][t]
        _groups_to_min_bitmap_count = [None] * tenants['tenant_group_count_map'][t]

        for g in range(tenants['tenant_group_count_map'][t]):
            if placement['tenant_groups_to_leaf_count'][t][g] > placement['num_bitmaps']:
                (_groups_categories_to_bitmap_map[g], _groups_leafs_to_category_map[g],
                 _groups_to_redundancy_map[g], _groups_to_min_bitmap_count[g]) = \
                    algorithms.dynmaic(
                        placement['tenant_groups_leafs_to_bitmap_map'][t][g],
                        placement['num_bitmaps'])

        _tenant_groups_categories_to_bitmap_map[t % chunk_size] = _groups_categories_to_bitmap_map
        _tenant_groups_leafs_to_category_map[t % chunk_size] = _groups_leafs_to_category_map
        _tenant_groups_to_redundancy_map[t % chunk_size] = _groups_to_redundancy_map
        _tenant_groups_to_min_bitmap_count[t % chunk_size] = _groups_to_min_bitmap_count

    return (_tenant_groups_categories_to_bitmap_map,
            _tenant_groups_leafs_to_category_map,
            _tenant_groups_to_redundancy_map,
            _tenant_groups_to_min_bitmap_count)


def _optimize(multi_threaded, tenants, placement, num_chunks, chunk_size):
    if not multi_threaded:
        _tenant_groups_categories_to_bitmap_map = [None] * tenants['num_tenants']
        _tenant_groups_leafs_to_category_map = [None] * tenants['num_tenants']
        _tenant_groups_to_redundancy_map = [None] * tenants['num_tenants']
        _tenant_groups_to_min_bitmap_count = [None] * tenants['num_tenants']

        for t in range(tenants['num_tenants']):
            _groups_categories_to_bitmap_map = [None] * tenants['tenant_group_count_map'][t]
            _groups_leafs_to_category_map = [None] * tenants['tenant_group_count_map'][t]
            _groups_to_redundancy_map = [None] * tenants['tenant_group_count_map'][t]
            _groups_to_min_bitmap_count = [None] * tenants['tenant_group_count_map'][t]

            for g in range(tenants['tenant_group_count_map'][t]):
                if placement['tenant_groups_to_leaf_count'][t][g] > placement['num_bitmaps']:
                    (_groups_categories_to_bitmap_map[g], _groups_leafs_to_category_map[g],
                     _groups_to_redundancy_map[g], _groups_to_min_bitmap_count[g]) = \
                        algorithms.dynmaic(
                            placement['tenant_groups_leafs_to_bitmap_map'][t][g],
                            placement['num_bitmaps'])

            _tenant_groups_categories_to_bitmap_map[t] = _groups_categories_to_bitmap_map
            _tenant_groups_leafs_to_category_map[t] = _groups_leafs_to_category_map
            _tenant_groups_to_redundancy_map[t] = _groups_to_redundancy_map
            _tenant_groups_to_min_bitmap_count[t] = _groups_to_min_bitmap_count
    else:
        optimize_pool = Pool(processes=num_chunks)

        optimize_results = optimize_pool.starmap(
            _optimize_chunk,
            [(tenants, placement, i, chunk_size) for i in range(num_chunks)])

        _tenant_groups_categories_to_bitmap_map = reduce(operator.concat, optimize_results[0])
        _tenant_groups_leafs_to_category_map = reduce(operator.concat, optimize_results[1])
        _tenant_groups_to_redundancy_map = reduce(operator.concat, optimize_results[2])
        _tenant_groups_to_min_bitmap_count = reduce(operator.concat, optimize_results[3])

    return (_tenant_groups_categories_to_bitmap_map,
            _tenant_groups_leafs_to_category_map,
            _tenant_groups_to_redundancy_map,
            _tenant_groups_to_min_bitmap_count)


def initialize(tenants, placement, multi_threaded=True, num_threads=2):
    if multi_threaded:
        num_chunks = num_threads
        if tenants['num_tenants'] % num_chunks != 0:
            raise Exception("number of threads should be a multiple of tenants count")
        chunk_size = int(tenants['num_tenants'] / num_chunks)

        print('optimization: no. of chunks %s' % num_chunks)
    else:
        num_chunks = 0
        chunk_size = 0

    (_tenant_groups_categories_to_bitmap_map,
     _tenant_groups_leafs_to_category_map,
     _tenant_groups_to_redundancy_map,
     _tenant_groups_to_min_bitmap_count) = _optimize(multi_threaded, tenants, placement, num_chunks, chunk_size)

    print('optimization: initialized.')

    return {'tenant_groups_categories_to_bitmap_map': _tenant_groups_categories_to_bitmap_map,
            'tenant_groups_leafs_to_category_map': _tenant_groups_leafs_to_category_map,
            'tenant_groups_to_redundancy_map': _tenant_groups_to_redundancy_map,
            'tenant_groups_to_min_bitmap_count': _tenant_groups_to_min_bitmap_count}
