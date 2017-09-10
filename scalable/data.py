from multiprocessing import Pool
import operator
from functools import reduce
import pandas as pd


def _get_leafs_for_all_tenants(cloud):
    leafs_for_all_tenants = pd.Series()

    for t in range(cloud['tenants']['num_tenants']):
        leafs_for_all_tenants = leafs_for_all_tenants.append(
            cloud['placement']['tenant_groups_to_leaf_count'][t], ignore_index=True)

    return leafs_for_all_tenants


def _get_percentage_hist_of_groups_covered_with_varying_bitmaps(cloud, leafs_for_all_tenants):
    hist = pd.cut(leafs_for_all_tenants, [i for i in range(cloud['placement']['num_bitmaps'] + 1)],
                  labels=[i for i in range(cloud['placement']['num_bitmaps'])]).value_counts()
    percentage_hist = hist / cloud['tenants']['tenant_group_count_map'].sum() * 100
    return percentage_hist.sort_index()


def _get_rules_for_all_leafs_chunk(cloud, chunk_id, chunk_size):
    base_index = chunk_id * chunk_size
    _rules_for_all_leafs = [0] * chunk_size

    for t in range(base_index, base_index + chunk_size):
        for g in range(cloud['tenants']['tenant_group_count_map'][t]):
            if cloud['placement']['tenant_groups_to_leaf_count'][t][g] > cloud['placement']['num_bitmaps']:
                for l in cloud['placement']['tenant_groups_to_leafs_map'][t][g]:
                    _rules_for_all_leafs[l % chunk_size] += 1

    return _rules_for_all_leafs


def _get_rules_for_all_leafs(multi_threaded, cloud, num_chunks, chunk_size):
    if not multi_threaded:
        _rules_for_all_leafs = [0] * cloud['network']['num_leafs']

        for t in range(cloud['tenants']['num_tenants']):
            for g in range(cloud['tenants']['tenant_group_count_map'][t]):
                if cloud['placement']['tenant_groups_to_leaf_count'][t][g] > cloud['placement']['num_bitmaps']:
                    for l in cloud['placement']['tenant_groups_to_leafs_map'][t][g]:
                        _rules_for_all_leafs[l] += 1
    else:
        rules_for_all_leafs_pool = Pool(processes=num_chunks)

        rules_for_all_leafs_results = rules_for_all_leafs_pool.starmap(
            _get_rules_for_all_leafs_chunk,
            [(cloud, i, chunk_size) for i in range(num_chunks)])

        _rules_for_all_leafs = reduce(operator.concat, rules_for_all_leafs_results)

    return pd.Series(_rules_for_all_leafs)


def _get_redundancy_for_all_tenants_chunk(chunk_id, chunk_size):
    pass


def _get_redundancy_for_all_tenants(multi_threaded, cloud):
    if not multi_threaded:
        redundancy_for_all_tenants = pd.Series()

        for t in range(cloud['tenants']['num_tenants']):
            for g in range(cloud['tenants']['tenant_group_count_map'][t]):
                if cloud['optimization']['tenant_groups_to_redundancy_map'][t][g] is not None:
                    redundancy_for_all_tenants = redundancy_for_all_tenants.append(
                        pd.Series(cloud['optimization']['tenant_groups_to_redundancy_map'][t][g]), ignore_index=True)
    else:
        pass




#
#
#
# class Data:
#     def __init__(self, cloud):
#         self.cloud = cloud
#
#         self.leafs_for_all_tenants = None
#         self._get_leafs_for_all_tenants()
#
#         self.percentage_hist_of_groups_covered_with_varying_bitmaps = None
#         self._get_percentage_hist_of_groups_covered_with_varying_bitmaps()
#
#         self.rules_for_all_leafs = None
#         self._get_rules_for_all_leafs()
#
#         self.redundancy_for_all_tenants = None
#         self._get_redundancy_for_all_tenants()
#
#         self.min_bitmaps_for_all_tenants = None
#         self._get_min_bitmaps_for_all_tenants()
#
#
#
#
#
#
#
#     def _get_redundancy_for_all_tenants(self):
#         self.redundancy_for_all_tenants = pd.Series()
#
#         for t in range(self.cloud.tenants.num_tenants):
#             for g in range(self.cloud.tenants.tenant_group_count_map[t]):
#                 if self.cloud.optimization.tenant_groups_to_redundancy_map[t][g] is not None:
#                     self.redundancy_for_all_tenants = self.redundancy_for_all_tenants.append(
#                         pd.Series(self.cloud.optimization.tenant_groups_to_redundancy_map[t][g]), ignore_index=True)
#
#     def _get_min_bitmaps_for_all_tenants(self):
#         self.min_bitmaps_for_all_tenants = pd.Series()
#
#         for t in range(self.cloud.tenants.num_tenants):
#             for g in range(self.cloud.tenants.tenant_group_count_map[t]):
#                 if self.cloud.optimization.tenant_groups_to_min_bitmap_count[t][g] is not None:
#                     self.min_bitmaps_for_all_tenants = self.min_bitmaps_for_all_tenants.append(
#                         pd.Series(self.cloud.optimization.tenant_groups_to_min_bitmap_count[t][g]), ignore_index=True)
