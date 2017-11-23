from simulation.algorithms.common import min_k_union_random as min_k_union


def run(data, max_bitmaps, leafs_to_rules_count_map, max_rules_per_leaf, probability=1.0 * 2 / 3):
    leaf_count = data['leaf_count']
    if leaf_count <= max_bitmaps:
        return

    leafs_map = data['leafs_map']

    # Sort leafs based on their flow table size (descending order)
    ordered_leafs_list = sorted(leafs_map.items(), key=lambda item: leafs_to_rules_count_map[item[0]], reverse=True)

    # Find out the no. of leafs who have used up all their flow table space
    num_leafs_with_no_space = sum(1 for (l, _) in ordered_leafs_list
                                  if leafs_to_rules_count_map[l] >= max_rules_per_leaf)

    # If no. of leafs with no space is less than or equal to the no. of available bitmaps then assign them a bitmap ...
    if (num_leafs_with_no_space - max_bitmaps) <= 0:
        for i in range(max_bitmaps):
            l, _ = ordered_leafs_list[i]
            leaf = leafs_map[l]
            leaf['has_bitmap'] = i

        for i in range(max_bitmaps, leaf_count):
            l, _ = ordered_leafs_list[i]
            leaf = leafs_map[l]
            leaf['has_rule'] = True
            leafs_to_rules_count_map[l] += 1

    # If no. of leafs with no space is greater than the no. of available bitmaps then assign them a bitmap and
    # rest the default bitmap ...
    else:
        ordered_leafs_with_no_space = [l for l, _ in ordered_leafs_list[:num_leafs_with_no_space]]
        default_bitmap, default_leafs = min_k_union(leafs_map, ordered_leafs_with_no_space,
                                                    num_leafs_with_no_space - max_bitmaps, probability)

        for i, l in enumerate(ordered_leafs_with_no_space):
            leaf = leafs_map[l]
            leaf['has_bitmap'] = i

        for l in default_leafs:
            leaf = leafs_map[l]
            leaf['~bitmap'] = default_bitmap ^ leaf['bitmap']

        data['default_bitmap'] = default_bitmap

        for i in range(num_leafs_with_no_space, leaf_count):
            l, _ = ordered_leafs_list[i]
            leaf = leafs_map[l]
            leaf['has_rule'] = True
            leafs_to_rules_count_map[l] += 1
