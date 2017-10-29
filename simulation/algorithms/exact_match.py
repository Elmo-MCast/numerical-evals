from bitstring import BitArray


def run(data, max_bitmaps, leafs_to_rules_count_map, max_rules_per_leaf, num_hosts_per_leaf):
    leafs_map = data['leafs_map']

    bitmap_to_leafs_map = dict()
    for leaf in leafs_map:
        if leafs_map[leaf]['bitmap'].hex in bitmap_to_leafs_map:
            bitmap_to_leafs_map[leafs_map[leaf]['bitmap'].hex] += [leaf]
        else:
            bitmap_to_leafs_map[leafs_map[leaf]['bitmap'].hex] = [leaf]

    ordered_bitmap_list = sorted(bitmap_to_leafs_map.items(), key=lambda item: len(item[1]), reverse=True)

    pass

    # num_leafs_with_no_space = 0
    # if max_rules_per_leaf > 0:
    #     for i, (l, _) in enumerate(ordered_leafs_list):
    #         if leafs_to_rules_count_map[l] >= max_rules_per_leaf:
    #             num_leafs_with_no_space += 1
    #         else:
    #             break
    #
    # if (num_leafs_with_no_space - max_bitmaps) <= 0:
    #     for i in range(max_bitmaps):
    #         l, _ = ordered_leafs_list[i]
    #         leafs_map[l]['has_bitmap'] = True
    #         leafs_map[l]['has_rule'] = False
    #
    #     for i in range(max_bitmaps, data['leaf_count']):
    #         l, _ = ordered_leafs_list[i]
    #         leafs_map[l]['has_bitmap'] = False
    #         leafs_map[l]['has_rule'] = True
    #         leafs_to_rules_count_map[l] += 1
    #
    #     data['r'] = 0
    #
    # elif (num_leafs_with_no_space - max_bitmaps) == 1:
    #     for i in range(max_bitmaps):
    #         l, _ = ordered_leafs_list[i]
    #         leafs_map[l]['has_bitmap'] = True
    #         leafs_map[l]['has_rule'] = False
    #
    #     data['default_bitmap'] = BitArray(num_hosts_per_leaf)
    #     l, _ = ordered_leafs_list[max_bitmaps]
    #     leafs_map[l]['has_bitmap'] = False
    #     leafs_map[l]['has_rule'] = False
    #     data['default_bitmap'] |= leafs_map[l]['bitmap']
    #     data['r'] = 0
    #
    #     for i in range(num_leafs_with_no_space, data['leaf_count']):
    #         l, _ = ordered_leafs_list[i]
    #         leafs_map[l]['has_bitmap'] = False
    #         leafs_map[l]['has_rule'] = True
    #         leafs_to_rules_count_map[l] += 1
    #
    # else:  # (num_leafs_with_no_space - max_bitmaps) >= 2
    #     # TODO: talk to Ori for a heuristic for this.
    #     for i in range(max_bitmaps):
    #         l, _ = ordered_leafs_list[i]
    #         leafs_map[l]['has_bitmap'] = True
    #         leafs_map[l]['has_rule'] = False
    #
    #     data['default_bitmap'] = BitArray(num_hosts_per_leaf)
    #     for i in range(max_bitmaps, num_leafs_with_no_space):
    #         l, _ = ordered_leafs_list[i]
    #         leafs_map[l]['has_bitmap'] = False
    #         leafs_map[l]['has_rule'] = False
    #         data['default_bitmap'] |= leafs_map[l]['bitmap']
    #
    #     data['r'] = 0
    #     for i in range(max_bitmaps, num_leafs_with_no_space):
    #         l, _ = ordered_leafs_list[i]
    #         data['r'] += sum(data['default_bitmap'] ^ leafs_map[l]['bitmap'])
    #
    #     for i in range(num_leafs_with_no_space, data['leaf_count']):
    #         l, _ = ordered_leafs_list[i]
    #         leafs_map[l]['has_bitmap'] = False
    #         leafs_map[l]['has_rule'] = True
    #         leafs_to_rules_count_map[l] += 1

