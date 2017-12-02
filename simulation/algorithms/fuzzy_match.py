from math import ceil
from simulation.utils import popcount
from simulation.algorithms.common import min_k_union


def run(data, max_bitmaps, max_leafs_per_bitmap, redundancy_per_bitmap, leafs_to_rules_count_map, max_rules_per_leaf):
    leafs_map = data['leafs_map']
    if len(leafs_map) <= max_bitmaps:
        return

    unassigned_leafs = [l for l in leafs_map]
    num_unassigned_bitmaps = max_bitmaps

    # Assign leafs to bitmaps
    for i in range(max_bitmaps):
        num_leafs_per_bitmap = int(ceil(1.0 * len(unassigned_leafs) / num_unassigned_bitmaps))
        for k in range(min(max_leafs_per_bitmap, num_leafs_per_bitmap), 0, -1):
            min_k_bitmap, min_k_leafs = min_k_union(leafs_map, unassigned_leafs, k)
            redundancy = sum([popcount(min_k_bitmap ^ leafs_map[l]['bitmap']) for l in min_k_leafs])
            if redundancy <= redundancy_per_bitmap:
                for l in min_k_leafs:
                    leaf = leafs_map[l]
                    leaf['has_bitmap'] = i
                    leaf['~bitmap'] = min_k_bitmap ^ leaf['bitmap']
                break
            else:
                unassigned_leafs += min_k_leafs
        num_unassigned_bitmaps -= 1

    # Add a rule or assign leafs to default bitmap
    default_bitmap = 0
    for l in unassigned_leafs:
        leaf = leafs_map[l]
        if leafs_to_rules_count_map[l] < max_rules_per_leaf:  # Add a rule in leaf
            leaf['has_rule'] = True
            leafs_to_rules_count_map[l] += 1
        else:  # Assign leaf to default bitmap
            default_bitmap |= leaf['bitmap']

    # Calculate redundancy for leafs assigned to default bitmap
    for l in unassigned_leafs:
        leaf = leafs_map[l]
        if 'has_rule' not in leaf:
            leaf['~bitmap'] = default_bitmap ^ leaf['bitmap']

    data['default_bitmap'] = default_bitmap
