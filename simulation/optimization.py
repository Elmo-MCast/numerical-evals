from simulation import algorithms


class Optimization:
    def __init__(self, network, tenants, placement):
        self.network = network
        self.tenants = tenants
        self.placement = placement

        self.tenant_groups_categories_to_bitmap_map = None
        self.tenant_groups_leafs_to_category_map = None
        self.tenant_groups_to_redundancy_map = None
        self.tenant_groups_to_min_bitmap_count = None

        self._optimize()

        print('optimization: initialized.')

    def _optimize(self):
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
