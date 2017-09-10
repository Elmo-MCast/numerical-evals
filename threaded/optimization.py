import operator
from functools import reduce
from threading import Thread

from threaded import algorithms


class Optimization:
    def __init__(self, network, tenants, placement, multi_threaded=True, num_threads=2):
        self.network = network
        self.tenants = tenants
        self.placement = placement
        self.multi_threaded = multi_threaded
        self.num_threads = num_threads

        if self.multi_threaded:
            self.num_chunks = self.num_threads
            if self.tenants.num_tenants % self.num_chunks != 0:
                raise Exception("number of threads should be a multiple of tenants count")
            self.chunk_size = int(self.tenants.num_tenants / self.num_chunks)

            # print('optimization: no. of chunks %s' % self.num_chunks)

        self.tenant_groups_categories_to_bitmap_map = None
        self.tenant_groups_leafs_to_category_map = None
        self.tenant_groups_to_redundancy_map = None
        self.tenant_groups_to_min_bitmap_count = None

        self._optimize()

        print('optimization: initialized.')

    def _optimize_chunk(self,
                        tenant_groups_categories_to_bitmap_map_chunks,
                        tenant_groups_leafs_to_category_map_chunks,
                        tenant_groups_to_redundancy_map_chunks,
                        tenant_groups_to_min_bitmap_count_chunks, chunk_id, chunk_size):
        base_index = chunk_id * chunk_size
        tenant_groups_categories_to_bitmap_map = [None] * chunk_size
        tenant_groups_leafs_to_category_map = [None] * chunk_size
        tenant_groups_to_redundancy_map = [None] * chunk_size
        tenant_groups_to_min_bitmap_count = [None] * chunk_size

        for t in range(base_index, base_index + chunk_size):
            _groups_categories_to_bitmap_map = [None] * self.tenants.tenant_group_count_map[t]
            _groups_leafs_to_category_map = [None] * self.tenants.tenant_group_count_map[t]
            _groups_to_redundancy_map = [None] * self.tenants.tenant_group_count_map[t]
            _groups_to_min_bitmap_count = [None] * self.tenants.tenant_group_count_map[t]

            for g in range(self.tenants.tenant_group_count_map[t]):
                if self.placement.tenant_groups_to_leaf_count[t][g] > self.placement.num_bitmaps:
                    (_groups_categories_to_bitmap_map[g], _groups_leafs_to_category_map[g],
                     _groups_to_redundancy_map[g], _groups_to_min_bitmap_count[g]) = \
                        algorithms.dynmaic(
                            self.placement.tenant_groups_leafs_to_bitmap_map[t][g],
                            self.placement.num_bitmaps)

            tenant_groups_categories_to_bitmap_map[t % chunk_size] = _groups_categories_to_bitmap_map
            tenant_groups_leafs_to_category_map[t % chunk_size] = _groups_leafs_to_category_map
            tenant_groups_to_redundancy_map[t % chunk_size] = _groups_to_redundancy_map
            tenant_groups_to_min_bitmap_count[t % chunk_size] = _groups_to_min_bitmap_count

        tenant_groups_categories_to_bitmap_map_chunks[chunk_id] = tenant_groups_categories_to_bitmap_map
        tenant_groups_leafs_to_category_map_chunks[chunk_id] = tenant_groups_leafs_to_category_map
        tenant_groups_to_redundancy_map_chunks[chunk_id] = tenant_groups_to_redundancy_map
        tenant_groups_to_min_bitmap_count_chunks[chunk_id] = tenant_groups_to_min_bitmap_count

    def _optimize(self):
        if not self.multi_threaded:
            self.tenant_groups_categories_to_bitmap_map = [None] * self.tenants.num_tenants
            self.tenant_groups_leafs_to_category_map = [None] * self.tenants.num_tenants
            self.tenant_groups_to_redundancy_map = [None] * self.tenants.num_tenants
            self.tenant_groups_to_min_bitmap_count = [None] * self.tenants.num_tenants

            for t in range(self.tenants.num_tenants):
                _groups_categories_to_bitmap_map = [None] * self.tenants.tenant_group_count_map[t]
                _groups_leafs_to_category_map = [None] * self.tenants.tenant_group_count_map[t]
                _groups_to_redundancy_map = [None] * self.tenants.tenant_group_count_map[t]
                _groups_to_min_bitmap_count = [None] * self.tenants.tenant_group_count_map[t]

                for g in range(self.tenants.tenant_group_count_map[t]):
                    if self.placement.tenant_groups_to_leaf_count[t][g] > self.placement.num_bitmaps:
                        (_groups_categories_to_bitmap_map[g], _groups_leafs_to_category_map[g],
                         _groups_to_redundancy_map[g], _groups_to_min_bitmap_count[g]) = \
                            algorithms.dynmaic(
                                self.placement.tenant_groups_leafs_to_bitmap_map[t][g],
                                self.placement.num_bitmaps)

                self.tenant_groups_categories_to_bitmap_map[t] = _groups_categories_to_bitmap_map
                self.tenant_groups_leafs_to_category_map[t] = _groups_leafs_to_category_map
                self.tenant_groups_to_redundancy_map[t] = _groups_to_redundancy_map
                self.tenant_groups_to_min_bitmap_count[t] = _groups_to_min_bitmap_count
        else:
            tenant_groups_categories_to_bitmap_map_chunks = [None] * self.num_chunks
            tenant_groups_leafs_to_category_map_chunks = [None] * self.num_chunks
            tenant_groups_to_redundancy_map_chunks = [None] * self.num_chunks
            tenant_groups_to_min_bitmap_count_chunks = [None] * self.num_chunks
            threads = [None] * self.num_chunks

            for i in range(self.num_chunks):
                threads[i] = Thread(target=self._optimize_chunk,
                                    args=(tenant_groups_categories_to_bitmap_map_chunks,
                                          tenant_groups_leafs_to_category_map_chunks,
                                          tenant_groups_to_redundancy_map_chunks,
                                          tenant_groups_to_min_bitmap_count_chunks, i, self.chunk_size))
                threads[i].start()

            for i in range(self.num_chunks):
                threads[i].join()

            self.tenant_groups_categories_to_bitmap_map = \
                reduce(operator.concat, tenant_groups_categories_to_bitmap_map_chunks)
            self.tenant_groups_leafs_to_category_map = \
                reduce(operator.concat, tenant_groups_leafs_to_category_map_chunks)
            self.tenant_groups_to_redundancy_map = \
                reduce(operator.concat, tenant_groups_to_redundancy_map_chunks)
            self.tenant_groups_to_min_bitmap_count = \
                reduce(operator.concat, tenant_groups_to_min_bitmap_count_chunks)
