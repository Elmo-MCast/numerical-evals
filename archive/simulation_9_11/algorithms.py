from bitstring import BitArray


# 1. Dynamic Programming

def _ones(bitmap):
    # counts the number of ones in a bitmap
    count = len([bit for bit in bitmap if bit == 1])
    return count


def _dp(bitmaps, max_bitmaps):  # dynamic programming algorithm
    # find categories serving the demands of bitmaps with a minimal redundant traffic
    G = max_bitmaps
    Q = len(bitmaps)
    W = len(bitmaps[0])

    max_demand = Q * W * 2
    bitmaps_count = [_ones(bitmap) for bitmap in bitmaps]

    R = [[max_demand for _ in range(G + 1)] for _ in range(Q + 1)]
    Y = [[[] for _ in range(G + 1)] for _ in range(Q + 1)]

    for g in range(0, G + 1):
        R[0][g] = 0
        Y[0][g] = []
    for g in range(1, G + 1):
        R[1][g] = 0
        Y[1][g] = [1]

    for q in range(2, Q + 1):
        # serving the first q masks
        for g in range(1, G + 1):
            # using at most g masks
            r = max_demand
            if R[q][g - 1] == 0:
                R[q][g] = 0
                Y[q][g] = Y[q][g - 1] + [0]
                continue
            for j in range(1, q + 1):
                r = R[q - j][g - 1]
                r += sum([bitmaps_count[q - 1] - bitmaps_count[q - k] for k in range(1, j + 1)])
                if r <= R[q][g]:
                    R[q][g] = r
                    Y[q][g] = Y[q - j][g - 1] + [j]

    category_bitmaps = []
    c = 0
    for g in range(G):
        c += Y[Q][G][g]
        category_bitmaps.append(bitmaps[c - 1])

    leaf_to_category_list = [-1 for _ in range(Q)]
    c = 0
    for g in range(1, G + 1):
        for x in range(c, c + Y[Q][G][g - 1]):
            leaf_to_category_list[x] = g
        c += Y[Q][G][g - 1]

    # min_bitmaps = -1
    min_bitmaps = max_bitmaps
    r = R[Q][G]
    if r == 0:
        min_bitmaps = max(leaf_to_category_list)

    return category_bitmaps, leaf_to_category_list, r, min_bitmaps


def _post_dp(max_bitmaps, min_bitmaps, category_bitmaps, leaf_to_category_list, leaf_to_has_rule_list):
    category_to_leafs_map = dict()
    for v, k in enumerate(leaf_to_category_list):
        if k in category_to_leafs_map:
            category_to_leafs_map[k].append(v)
        else:
            category_to_leafs_map[k] = [v]
    category_to_leafs_tuple = sorted(category_to_leafs_map.items(), key=lambda item: len(item[1]))

    _min_bitmaps = min_bitmaps
    _unused_bitmaps = max_bitmaps - min_bitmaps
    for category, l_offsets in category_to_leafs_tuple:
        l_offsets_length = len(l_offsets)

        if l_offsets_length == 1:
            leaf_to_has_rule_list[l_offsets[0]] = False
        else:
            for i in range(l_offsets_length):
                if _unused_bitmaps > 0:
                    if (i + 1) == l_offsets_length:
                        leaf_to_has_rule_list[l_offsets[i]] = False
                    else:
                        category_bitmaps += [category_bitmaps[category - 1]]
                        leaf_to_category_list[l_offsets[i]] = len(category_bitmaps)
                        leaf_to_has_rule_list[l_offsets[i]] = False
                        _unused_bitmaps -= 1
                        _min_bitmaps += 1
                else:
                    if (i + 1) == l_offsets_length:
                        leaf_to_has_rule_list[l_offsets[i]] = False
                    break

    return _min_bitmaps


def dynmaic(data, max_bitmaps, post_process=True):
    leafs_map = data['leafs_map']
    ordered_leafs_list = sorted(leafs_map.items(), key=lambda item: item[1]['bitmap']['sorted'].bin)
    input_bitmaps = [x['bitmap']['sorted'] for _, x in ordered_leafs_list]

    category_bitmaps, leaf_to_category_list, r, min_bitmaps = _dp(input_bitmaps, max_bitmaps)
    category_bitmaps = category_bitmaps[:min_bitmaps]

    leaf_to_has_rule_list = [True] * len(leaf_to_category_list)

    if post_process:
        min_bitmaps = _post_dp(max_bitmaps, min_bitmaps, category_bitmaps, leaf_to_category_list,
                               leaf_to_has_rule_list)

    data['category_bitmaps'] = category_bitmaps
    data['r'] = r
    data['min_bitmaps'] = min_bitmaps

    for i, (l, _) in enumerate(ordered_leafs_list):
        leafs_map[l]['category'] = leaf_to_category_list[i] - 1
        leafs_map[l]['has_rule'] = leaf_to_has_rule_list[i]


if __name__ == "__main__":
    sample_bitmaps = [BitArray('0b1000'), BitArray('0b1000'), BitArray('0b1000'), BitArray('0b1000'),
                      BitArray('0b1100'), BitArray('0b1100'),
                      BitArray('0b1110'), BitArray('0b1110'), BitArray('0b1110'), BitArray('0b1110'),
                      BitArray('0b1111'), BitArray('0b1111'), BitArray('0b1111')]

    max_bitmaps = 10

    category_bitmaps, leaf_to_category_list, r, min_bitmaps = _dp(sample_bitmaps, max_bitmaps)
    category_bitmaps = category_bitmaps[:min_bitmaps]

    leaf_to_has_rule_list = [True] * len(leaf_to_category_list)

    print('input_bitmaps: %s' % [bitmap.bin for bitmap in sample_bitmaps])
    print('len(input_bitmaps): %s' % len(sample_bitmaps))
    print('max_bitmaps: %s' % max_bitmaps)

    print('\n\ndp step:')
    print('category_bitmaps: %s' % [bitmap.bin for bitmap in category_bitmaps])
    print('redundancy: %s' % r)
    print('leaf_to_category_list: %s' % leaf_to_category_list)
    print('leaf_to_has_rule_list: %s' % leaf_to_has_rule_list)
    print('min_bitmaps: %s' % min_bitmaps)

    min_bitmaps = _post_dp(max_bitmaps, min_bitmaps, category_bitmaps,
                           leaf_to_category_list, leaf_to_has_rule_list)

    print('\n\npost dp step:')

    print('category_bitmaps: %s' % [bitmap.bin for bitmap in category_bitmaps])
    print('redundancy: %s' % r)
    print('leaf_to_category_list: %s' % leaf_to_category_list)
    print('leaf_to_has_rule_list: %s' % leaf_to_has_rule_list)
    print('min_bitmaps: %s' % min_bitmaps)