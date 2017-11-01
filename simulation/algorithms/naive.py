import numpy as np


def min_k_union(leafs_map, leafs, num_hosts_per_leaf, k):
    _bitmap = np.array([0] * num_hosts_per_leaf)
    _leafs = []
    for _ in range(k):
        leaf = min(leafs, key=lambda l: np.count_nonzero(leafs_map[l]['bitmap'] | _bitmap))
        leafs.remove(leaf)
        _bitmap |= leafs_map[leaf]['bitmap']
        _leafs += [leaf]
    return _bitmap, _leafs


def run(data, max_bitmaps, leafs_to_rules_count_map, max_rules_per_leaf, num_hosts_per_leaf):
    if data['leaf_count'] <= max_bitmaps:
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

    # If no. of leafs with no space is less than the no. of available bitmaps then assign them a bitmap ...
    if (num_leafs_with_no_space - max_bitmaps) <= 0:
        for i in range(max_bitmaps):
            l, _ = ordered_leafs_list[i]
            leafs_map[l]['has_bitmap'] = True
            leafs_map[l]['has_rule'] = False

        for i in range(max_bitmaps, data['leaf_count']):
            l, _ = ordered_leafs_list[i]
            leafs_map[l]['has_bitmap'] = False
            leafs_map[l]['has_rule'] = True
            leafs_to_rules_count_map[l] += 1

        data['r'] = 0

    # If no. of leafs with no space is one more than the no. of available bitmaps then assign them a bitmap and
    # last one to the default bitmap ...
    elif (num_leafs_with_no_space - max_bitmaps) == 1:
        for i in range(max_bitmaps):
            l, _ = ordered_leafs_list[i]
            leafs_map[l]['has_bitmap'] = True
            leafs_map[l]['has_rule'] = False

        data['default_bitmap'] = np.array([0] * num_hosts_per_leaf)
        l, _ = ordered_leafs_list[max_bitmaps]
        leafs_map[l]['has_bitmap'] = False
        leafs_map[l]['has_rule'] = False
        data['default_bitmap'] |= leafs_map[l]['bitmap']
        data['r'] = 0

        for i in range(num_leafs_with_no_space, data['leaf_count']):
            l, _ = ordered_leafs_list[i]
            leafs_map[l]['has_bitmap'] = False
            leafs_map[l]['has_rule'] = True
            leafs_to_rules_count_map[l] += 1

    # If no. of leafs with no space is two or more than the no. of available bitmaps then assign them a bitmap and
    # rest the default bitmap ...
    else:  # (num_leafs_with_no_space - max_bitmaps) >= 2
        # Note: this problem is equivalent to MIN-K-UNION problem. I'm using a heuristic posted here:
        # https://stackoverflow.com/questions/12424155/given-n-sets-of-elements-find-minimal-union-of-m-sets

        ordered_leafs_with_no_space = [l for l, _ in ordered_leafs_list[:num_leafs_with_no_space]]
        default_bitmap, default_leafs = min_k_union(leafs_map, ordered_leafs_with_no_space, num_hosts_per_leaf,
                                                    num_leafs_with_no_space - max_bitmaps)

        for l in ordered_leafs_with_no_space:
            leafs_map[l]['has_bitmap'] = True
            leafs_map[l]['has_rule'] = False

        data['default_bitmap'] = default_bitmap
        for l in default_leafs:
            leafs_map[l]['has_bitmap'] = False
            leafs_map[l]['has_rule'] = False

        data['r'] = 0
        for l in default_leafs:
            leafs_map[l]['~bitmap'] = data['default_bitmap'] ^ leafs_map[l]['bitmap']
            data['r'] += np.count_nonzero(leafs_map[l]['~bitmap'])

        for i in range(num_leafs_with_no_space, data['leaf_count']):
            l, _ = ordered_leafs_list[i]
            leafs_map[l]['has_bitmap'] = False
            leafs_map[l]['has_rule'] = True
            leafs_to_rules_count_map[l] += 1