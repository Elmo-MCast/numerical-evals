import pandas as pd
import numpy as np


class Data:
    def __init__(self, cloud):
        self.network = cloud.data['network']
        self.tenants = cloud.data['tenants']
        self.tenants_maps = self.tenants['maps']
        self.placement = cloud.data['placement']

    def vm_count_for_all_tenants(self):
        return pd.Series([self.tenants_maps[t]['vm_count'] for t in range(self.tenants['num_tenants'])])

    def group_count_for_all_tenants(self):
        return pd.Series([self.tenants_maps[t]['group_count'] for t in range(self.tenants['num_tenants'])])

    def group_sizes_for_all_tenants(self):
        _group_sizes_for_all_tenants = []

        for t in range(self.tenants['num_tenants']):
            for g in range(self.tenants_maps[t]['group_count']):
                _group_sizes_for_all_tenants += [self.tenants_maps[t]['groups_map'][g]['size']]

        return pd.Series(_group_sizes_for_all_tenants)

    def leafs_for_all_groups_in_all_tenants(self):
        _leafs_for_all_groups_in_all_tenants = []

        for t in range(self.tenants['num_tenants']):
            for g in range(self.tenants_maps[t]['group_count']):
                _leafs_for_all_groups_in_all_tenants += [self.tenants_maps[t]['groups_map'][g]['leaf_count']]

        return pd.Series(_leafs_for_all_groups_in_all_tenants)

    def percentage_of_groups_covered_with_varying_bitmaps(self, num_bitmaps):
        categories = pd.cut(self.leafs_for_all_groups_in_all_tenants(), [i for i in range(-1, num_bitmaps + 1)],
                            right=True, labels=[i for i in range(0, num_bitmaps + 1)]).value_counts()
        percentage_categories = np.cumsum(categories.sort_index()).astype(np.double) / self.tenants['group_count'] * 100
        return percentage_categories

    def rules_for_all_leafs(self):
        return pd.Series(self.placement['maps']['leafs_to_rules_count'])

    def redundancy_for_all_groups_in_all_tenants(self):
        _redundancy_for_all_groups_in_all_tenants = []

        for t in range(self.tenants['num_tenants']):
            for g in range(self.tenants_maps[t]['group_count']):
                if self.tenants_maps[t]['groups_map'][g]['leaf_count'] > self.placement['num_bitmaps']:
                    _redundancy_for_all_groups_in_all_tenants += \
                        [self.tenants_maps[t]['groups_map'][g]['r'] /
                         (self.tenants_maps[t]['groups_map'][g]['r'] + self.tenants_maps[t]['groups_map'][g]['size'])
                         * 100]

        return pd.Series(_redundancy_for_all_groups_in_all_tenants)

    # def rules_for_all_leafs_pre_optimization(self):
    #     _rules_for_all_leafs = [0] * self.network['num_leafs']
    #
    #     for t in range(self.tenants['num_tenants']):
    #         for g in range(self.tenants_maps[t]['group_count']):
    #             if self.tenants_maps[t]['groups_map'][g]['leaf_count'] > self.placement['num_bitmaps']:
    #                 num_bitmaps = self.placement['num_bitmaps']
    #                 for l in self.tenants_maps[t]['groups_map'][g]['leafs']:
    #                     if num_bitmaps > 0:
    #                         num_bitmaps -= 1
    #                     else:
    #                         _rules_for_all_leafs[l] += 1
    #
    #     return pd.Series(_rules_for_all_leafs)
    #
    # def rules_for_all_groups_pre_optimization(self):
    #     _rules_for_all_groups_pre_optimization = []
    #
    #     for t in range(self.tenants['num_tenants']):
    #         for g in range(self.tenants_maps[t]['group_count']):
    #             _rules_for_all_groups_pre_optimization += [0]
    #             if self.tenants_maps[t]['groups_map'][g]['leaf_count'] > self.placement['num_bitmaps']:
    #                 num_bitmaps = self.placement['num_bitmaps']
    #                 for _ in self.tenants_maps[t]['groups_map'][g]['leafs']:
    #                     if num_bitmaps > 0:
    #                         num_bitmaps -= 1
    #                     else:
    #                         _rules_for_all_groups_pre_optimization[len(_rules_for_all_groups_pre_optimization) - 1] += 1
    #
    #     return pd.Series(_rules_for_all_groups_pre_optimization)
    #
    # def rules_for_all_groups_post_optimization(self):
    #     _rules_for_all_groups_post_optimization = []
    #
    #     for t in range(self.tenants['num_tenants']):
    #         for g in range(self.tenants_maps[t]['group_count']):
    #             _rules_for_all_groups_post_optimization += [0]
    #             if self.tenants_maps[t]['groups_map'][g]['leaf_count'] > self.placement['num_bitmaps']:
    #                 for l in self.tenants_maps[t]['groups_map'][g]['leafs']:
    #                     if self.tenants_maps[t]['groups_map'][g]['leafs_map'][l]['has_rule']:
    #                         _rules_for_all_groups_post_optimization[
    #                             len(_rules_for_all_groups_post_optimization) - 1] += 1
    #
    #     return pd.Series(_rules_for_all_groups_post_optimization)

