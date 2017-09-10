from bitstring import BitArray
from collections import OrderedDict


# Collection of Algorithms


# 1. Dummy

def dummy(leaf_bitmaps, max_bitmaps):
    return ([BitArray(len(leaf_bitmaps[list(leaf_bitmaps.keys())[0]]))] * max_bitmaps,
            {i: i for i in range(max_bitmaps)}, 10, len(leaf_bitmaps))


# 2. Dynamic Programming

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

    min_bitmaps = -1
    r = R[Q][G]
    if r == 0:
        min_bitmaps = max(leaf_to_category_list)
    return category_bitmaps, leaf_to_category_list, r, min_bitmaps


def dynmaic(leafs_to_bitmap_map, max_bitmaps):
    ordered_leaf_bitmaps = OrderedDict(sorted(leafs_to_bitmap_map.items(), key=lambda item: item[1]['sorted'].bin))
    input_bitmaps = [v['sorted'] for _, v in ordered_leaf_bitmaps.items()]

    category_bitmaps, leaf_to_category_list, r, min_bitmaps = _dp(input_bitmaps, max_bitmaps)

    leafs_to_category_map = {k: leaf_to_category_list[list(ordered_leaf_bitmaps.keys()).index(k)]
                             for k, _ in ordered_leaf_bitmaps.items()}

    return category_bitmaps, leafs_to_category_map, r, min_bitmaps


if __name__ == "__main__":
    sample_leaf_bitmaps_maps = {
        1: {'actual': BitArray('0b0001'),
            'sorted': BitArray('0b1000')},
        2: {'actual': BitArray('0b0110'),
            'sorted': BitArray('0b1100')},
        3: {'actual': BitArray('0b0010'),
            'sorted': BitArray('0b1000')},
        4: {'actual': BitArray('0b0100'),
            'sorted': BitArray('0b1000')},
        5: {'actual': BitArray('0b1111'),
            'sorted': BitArray('0b1111')},
        6: {'actual': BitArray('0b0111'),
            'sorted': BitArray('0b1110')},
        7: {'actual': BitArray('0b1010'),
            'sorted': BitArray('0b1100')},
        8: {'actual': BitArray('0b1111'),
            'sorted': BitArray('0b1111')},
        9: {'actual': BitArray('0b0100'),
            'sorted': BitArray('0b1000')},
        10: {'actual': BitArray('0b1111'),
             'sorted': BitArray('0b1111')},
        11: {'actual': BitArray('0b1011'),
             'sorted': BitArray('0b1110')},
        12: {'actual': BitArray('0b0111'),
             'sorted': BitArray('0b1110')},
        13: {'actual': BitArray('0b1101'),
             'sorted': BitArray('0b1110')}
    }

    dynmaic(sample_leaf_bitmaps_maps, 10)
