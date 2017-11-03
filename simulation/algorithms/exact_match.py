import numpy as np


def run(data, max_bitmaps, max_leafs_per_bitmap, leafs_to_rules_count_map, max_rules_per_leaf, num_hosts_per_leaf):
    if data['leaf_count'] <= max_bitmaps:
        return

    leafs_map = data['leafs_map']

    # Initializing default bitmap
    data['default_bitmap'] = np.array([0] * num_hosts_per_leaf)

    # Generating bitmaps-to-leaf mapping
    bitmap_to_leafs_map = dict()
    for l in leafs_map:
        if tuple(leafs_map[l]['bitmap']) in bitmap_to_leafs_map:
            bitmap_to_leafs_map[tuple(leafs_map[l]['bitmap'])] += [l]
        else:
            bitmap_to_leafs_map[tuple(leafs_map[l]['bitmap'])] = [l]

    # Sorting bitmaps-to-leaf mapping based on the number of leafs per bitmap (descending order)
    ordered_bitmap_list = sorted(bitmap_to_leafs_map.items(), key=lambda item: len(item[1]), reverse=True)

    # Assigning leafs to bitmaps, rules, and default bitmap
    bitmap_count = 0
    leafs_per_bitmap_count = 0
    leafs_budget_count = (max_bitmaps * max_leafs_per_bitmap) - max_bitmaps
    for _, leafs in ordered_bitmap_list:
        for l in leafs:
            if bitmap_count < max_bitmaps:  # Assign leaf to a bitmap
                leafs_map[l]['has_bitmap'] = True
                leafs_map[l]['has_rule'] = False
                leafs_per_bitmap_count += 1

                # Select next bitmap, when no. of leafs assigned is equal to (1 + leafs_budget_count)
                if leafs_per_bitmap_count == (1 + leafs_budget_count):
                    leafs_budget_count = 0
                    bitmap_count += 1
                    leafs_per_bitmap_count = 0
            else:
                if leafs_to_rules_count_map[l] < max_rules_per_leaf:  # Add a rule in leaf
                    leafs_map[l]['has_bitmap'] = False
                    leafs_map[l]['has_rule'] = True
                    leafs_to_rules_count_map[l] += 1
                else:  # Assign leaf to default bitmap
                    leafs_map[l]['has_bitmap'] = False
                    leafs_map[l]['has_rule'] = False
                    data['default_bitmap'] |= leafs_map[l]['bitmap']

        # Select next bitmap, if the current bitmap contains any leaf
        if bitmap_count < max_bitmaps and leafs_per_bitmap_count > 0:
            leafs_budget_count -= (leafs_per_bitmap_count - 1)
            bitmap_count += 1
            leafs_per_bitmap_count = 0

    for l in leafs_map:
        if not (leafs_map[l]['has_bitmap'] or leafs_map[l]['has_rule']):
            leafs_map[l]['~bitmap'] = data['default_bitmap'] ^ leafs_map[l]['bitmap']
