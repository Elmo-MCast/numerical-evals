from simulation.utils import popcount


def min_k_union(leafs_map, leafs, k):
    _bitmap = 0
    _leafs = []
    for _ in range(k):
        leaf = min(leafs, key=lambda l: popcount(leafs_map[l]['bitmap'] | _bitmap))
        leafs.remove(leaf)
        _bitmap |= leafs_map[leaf]['bitmap']
        _leafs += [leaf]
    return _bitmap, _leafs


def run(data, max_bitmaps, leafs_to_rules_count_map, max_rules_per_leaf):
    leaf_count = data['leaf_count']
    if leaf_count <= max_bitmaps:
        return

    leafs_map = data['leafs_map']

    # Sort leafs based on their flow table space (descending order)
    ordered_leafs_list = sorted(leafs_map.items(), key=lambda item: leafs_to_rules_count_map[item[0]], reverse=True)

    # Find out the no. of leafs who have used up all their flow table space
    num_leafs_with_no_space = 0
    if max_rules_per_leaf > 0:
        for (l, _) in ordered_leafs_list:
            if leafs_to_rules_count_map[l] >= max_rules_per_leaf:
                num_leafs_with_no_space += 1
            else:
                break

    # If no. of leafs with no space is less than or equal to the no. of available bitmaps then assign them a bitmap ...
    if (num_leafs_with_no_space - max_bitmaps) <= 0:
        for i in range(max_bitmaps):
            l, _ = ordered_leafs_list[i]
            leaf = leafs_map[l]
            leaf['has_bitmap'] = True

        for i in range(max_bitmaps, leaf_count):
            l, _ = ordered_leafs_list[i]
            leaf = leafs_map[l]
            leaf['has_rule'] = True
            leafs_to_rules_count_map[l] += 1

    # If no. of leafs with no space is greater than the no. of available bitmaps then assign them a bitmap and
    # rest the default bitmap ...
    else:  # (num_leafs_with_no_space - max_bitmaps) >= 1
        # Note: this problem is equivalent to MIN-K-UNION problem. I'm using a heuristic posted here:
        # https://stackoverflow.com/questions/12424155/given-n-sets-of-elements-find-minimal-union-of-m-sets

        ordered_leafs_with_no_space = [l for l, _ in ordered_leafs_list[:num_leafs_with_no_space]]
        default_bitmap, default_leafs = min_k_union(leafs_map, ordered_leafs_with_no_space,
                                                    num_leafs_with_no_space - max_bitmaps)

        for l in ordered_leafs_with_no_space:
            leaf = leafs_map[l]
            leaf['has_bitmap'] = True

        for l in default_leafs:
            leaf = leafs_map[l]
            leaf['~bitmap'] = default_bitmap ^ leaf['bitmap']

        data['default_bitmap'] = default_bitmap

        for i in range(num_leafs_with_no_space, leaf_count):
            l, _ = ordered_leafs_list[i]
            leaf = leafs_map[l]
            leaf['has_rule'] = True
            leafs_to_rules_count_map[l] += 1
