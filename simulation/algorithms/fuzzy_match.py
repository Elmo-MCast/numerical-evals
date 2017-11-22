from simulation.utils import popcount
from math import floor


def min_k_union(leafs_map, leafs, k):
    min_k_bitmap = 0
    min_k_leafs = []
    for _ in range(k):
        leaf = min(leafs, key=lambda l: popcount(leafs_map[l]['bitmap'] | min_k_bitmap))
        leafs.remove(leaf)
        min_k_bitmap |= leafs_map[leaf]['bitmap']
        min_k_leafs += [leaf]
    return min_k_bitmap, min_k_leafs


def run(data, max_bitmaps, max_leafs_per_bitmap, redundancy_per_bitmap, leafs_to_rules_count_map,
        max_rules_per_leaf):
    leaf_count = data['leaf_count']
    if leaf_count <= max_bitmaps:
        return

    leafs_map = data['leafs_map']
    leafs = [l for l in leafs_map]

    # Get packing of leafs per bitmap
    min_leafs_per_bitmap = floor(leaf_count / max_bitmaps)
    num_excess_leafs = leaf_count % max_bitmaps
    if (min_leafs_per_bitmap + (1 if num_excess_leafs > 0 else 0)) > max_leafs_per_bitmap:
        min_leafs_per_bitmap = max_leafs_per_bitmap
        num_excess_leafs = 0

    # Assign leafs to bitmaps
    for i in range(max_bitmaps):
        for j, k in enumerate(range(min_leafs_per_bitmap + (1 if num_excess_leafs > 0 else 0), 0, -1)):
            min_k_bitmap, min_k_leafs = min_k_union(leafs_map, leafs, k)
            redundancy = sum([popcount(min_k_bitmap ^ leafs_map[l]['bitmap']) for l in min_k_leafs])
            if redundancy <= redundancy_per_bitmap:
                for l in min_k_leafs:
                    leaf = leafs_map[l]
                    leaf['has_bitmap'] = i
                    leaf['~bitmap'] = min_k_bitmap ^ leaf['bitmap']

                num_excess_leafs -= (1 if j == 0 and num_excess_leafs > 0 else 0)
                break
            else:
                leafs += min_k_leafs

    # Add a rule or assign leafs to default bitmap
    default_bitmap = 0
    for l in leafs:
        leaf = leafs_map[l]
        if leafs_to_rules_count_map[l] < max_rules_per_leaf:  # Add a rule in leaf
            leaf['has_rule'] = True
            leafs_to_rules_count_map[l] += 1
        else:  # Assign leaf to default bitmap
            default_bitmap |= leaf['bitmap']

    # Calculate redundancy for leafs assigned to default bitmap
    for l in leafs:
        leaf = leafs_map[l]
        if 'has_rule' not in leaf:
            leaf['~bitmap'] = default_bitmap ^ leaf['bitmap']

    data['default_bitmap'] = default_bitmap
