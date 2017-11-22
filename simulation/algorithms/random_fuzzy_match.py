from simulation.utils import popcount
import random


def min_k_union(leafs_map, leafs, k, prob):
    min_k_bitmap = 0
    min_k_leafs = []

    for _ in range(k):
        leaf = min(leafs, key=lambda l: popcount(leafs_map[l]['bitmap'] | min_k_bitmap))
        if not random.random() < prob:
            leaf = min(filter(leaf.__ne__, leafs), key=lambda l: popcount(leafs_map[l]['bitmap'] | min_k_bitmap))
        leafs.remove(leaf)
        min_k_bitmap |= leafs_map[leaf]['bitmap']
        min_k_leafs += [leaf]
    return min_k_bitmap, min_k_leafs


def run(data, max_bitmaps, max_leafs_per_bitmap, redundancy_per_bitmap, leafs_to_rules_count_map,
        max_rules_per_leaf, prob=1/3):
    leaf_count = data['leaf_count']
    if leaf_count <= max_bitmaps:
        return

    leafs_map = data['leafs_map']
    leafs = [l for l in leafs_map]

    # Get packing of leafs per bitmap
    num_leafs_per_bitmap = int(leaf_count / max_bitmaps)
    num_excess_leafs = leaf_count % max_bitmaps
    if (num_leafs_per_bitmap + (1 if num_excess_leafs > 0 else 0)) > max_leafs_per_bitmap:
        num_leafs_per_bitmap = max_leafs_per_bitmap
        num_excess_leafs = 0

    # Assign leafs to bitmaps
    for i in range(max_bitmaps):
        running_num_leafs_per_bitmap = num_leafs_per_bitmap
        if num_excess_leafs > 0:
            running_num_leafs_per_bitmap += 1

        for k in range(running_num_leafs_per_bitmap, 0, -1):
            min_k_bitmap, min_k_leafs = min_k_union(leafs_map, leafs, k, prob)
            redundancy = sum([popcount(min_k_bitmap ^ leafs_map[l]['bitmap']) for l in min_k_leafs])
            if redundancy <= redundancy_per_bitmap:
                for l in min_k_leafs:
                    leaf = leafs_map[l]
                    leaf['has_bitmap'] = i
                    leaf['~bitmap'] = min_k_bitmap ^ leaf['bitmap']

                if k == running_num_leafs_per_bitmap and num_excess_leafs > 0:
                    num_excess_leafs -= 1
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
