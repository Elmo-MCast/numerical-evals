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


def _get_rules_for_all_leafs(cloud):
    _rules_for_all_leafs = [0] * cloud['network']['num_leafs']

    for t in range(cloud['tenants']['num_tenants']):
        for g in range(cloud['tenants']['tenant_group_count_map'][t]):
            if cloud['placement']['tenant_groups_to_leaf_count'][t][g] > cloud['placement']['num_bitmaps']:
                for l in cloud['placement']['tenant_groups_to_leafs_map'][t][g]:
                    _rules_for_all_leafs[l] += 1

    return pd.Series(_rules_for_all_leafs)


def _get_redundancy_for_all_tenants(cloud):
    _redundancy_for_all_tenants = pd.Series()

    for t in range(cloud['tenants']['num_tenants']):
        for g in range(cloud['tenants']['tenant_group_count_map'][t]):
            if cloud['optimization']['tenant_groups_to_redundancy_map'][t][g] is not None:
                _redundancy_for_all_tenants = _redundancy_for_all_tenants.append(
                    pd.Series(cloud['optimization']['tenant_groups_to_redundancy_map'][t][g]), ignore_index=True)

    return _redundancy_for_all_tenants


def _get_min_bitmaps_for_all_tenants(cloud):
    _min_bitmaps_for_all_tenants = pd.Series()

    for t in range(cloud['tenants']['num_tenants']):
        for g in range(cloud['tenants']['tenant_group_count_map'][t]):
            if cloud['optimization']['tenant_groups_to_min_bitmap_count'][t][g] is not None:
                _min_bitmaps_for_all_tenants = _min_bitmaps_for_all_tenants.append(
                    pd.Series(cloud['optimization']['tenant_groups_to_min_bitmap_count'][t][g]), ignore_index=True)

    return _min_bitmaps_for_all_tenants


def initialize(cloud):
    _leafs_for_all_tenants = _get_leafs_for_all_tenants(cloud)

    _percentage_hist_of_groups_covered_with_varying_bitmaps = \
        _get_percentage_hist_of_groups_covered_with_varying_bitmaps(cloud, _leafs_for_all_tenants)

    _rules_for_all_leafs = _get_rules_for_all_leafs(cloud)

    # _redundancy_for_all_tenants = _get_redundancy_for_all_tenants(cloud)

    # _min_bitmaps_for_all_tenants = _get_min_bitmaps_for_all_tenants(cloud)

    print('data: initialized.')

    return {'leafs_for_all_tenants': _leafs_for_all_tenants,
            'percentage_hist_of_groups_covered_with_varying_bitmaps':
                _percentage_hist_of_groups_covered_with_varying_bitmaps,
            'rules_for_all_leafs': _rules_for_all_leafs,
            # 'redundancy_for_all_tenants': _redundancy_for_all_tenants,
            # 'min_bitmaps_for_all_tenants': _min_bitmaps_for_all_tenants,
            'cloud': cloud}
