DEBUG = False


def _organize_bitmaps(input_bitmaps):
    # reorder the bits to follow the algorithm assumptions
    if not input_bitmaps:
        return
    Q = len(input_bitmaps)
    W = len(input_bitmaps[0])
    cnt = [len([j for j in range(Q) if input_bitmaps[j][i] == "1"]) for i in range(W)]

    perm = []
    while len(perm) < W:
        max_cnt = 0
        for i in range(W):
            if cnt[i] > max_cnt:
                ind = i
                max_cnt = cnt[i]
        perm.append(ind)
        cnt[ind] = 0

    output_bitmaps = []
    for j in range(Q):
        bitmap = ""
        for i in range(W):
            bitmap += input_bitmaps[j][perm[i]]
        output_bitmaps.append(bitmap)
    output_bitmaps.sort()
    return output_bitmaps, perm


def _ones(bitmap):
    # counts the number of ones in a bitmap
    c = len([x for x in bitmap if x == "1"])
    return c


def dp_algorithm(switch_bitmaps, num_bitmaps):
    # find groups serving the demands of leaf_bitmaps with a minimal redundant traffic
    G = num_bitmaps
    Q = len(switch_bitmaps)
    W = len(switch_bitmaps[0])
    bitmaps, perm = _organize_bitmaps(switch_bitmaps)
    bitmaps_num = [_ones(bitmap) for bitmap in bitmaps]

    if DEBUG:
        print(bitmaps_num, bitmaps)
    print(bitmaps)

    max_demand = Q * W * 2
    if DEBUG:
        print("max:", max_demand)

    R = [[max_demand for _ in range(G + 1)] for _ in range(Q + 1)]
    Y = [[[] for _ in range(G + 1)] for _ in range(Q + 1)]

    for g in range(0, G + 1):
        R[0][g] = 0
        Y[0][g] = []
    for g in range(1, G + 1):
        R[1][g] = 0
        Y[1][g] = [1]

    if DEBUG:
        print(Y)
        print()

    for q in range(2, Q + 1):
        # serving the first q masks
        for g in range(1, G + 1):
            # using at most g masks
            r = max_demand
            for j in range(1, q + 1):
                r = R[q - j][g - 1]
                if DEBUG:
                    print("!", q, g, r, "  ", "(", q-j, g-1, ")")
                r += sum([bitmaps_num[q - 1] - bitmaps_num[q - k] for k in range(1, j + 1)])
                if DEBUG:
                    print(r)
                if r <= R[q][g]:
                    R[q][g] = r
                    Y[q][g] = Y[q - j][g - 1] + [j]

                    if DEBUG:
                        print(q, R[:q+1])
                        print(q, Y[:q+1])
                        print()
                        print()

                        print("Q, G:", Q, G)
                        print("1:", Y[1], R[1])
                        print("Y:", Y[Q][G])
                        print("R:", R[Q][G])

    group_bitmaps = []
    c = 0
    for g in range(G):
        c += Y[Q][G][g]
        group_bitmaps.append(bitmaps[c - 1])

    switch_to_group_map = [-1 for _ in range(Q)]
    c = 0
    for g in range(1, G + 1):
        for x in range(c, c + Y[Q][G][g - 1]):
            switch_to_group_map[x] = g
        c += Y[Q][G][g - 1]
    r = R[Q][G]
    return group_bitmaps, switch_to_group_map, r


if __name__ == "__main__":
    sample_switch_bitmaps = ["1000", "1100", "1000", "1000", "1111", "1110", "1100",
                             "1111", "1000", "1111", "1110", "1110", "1110"]

    # sample_switch_bitmaps = ["1000", "1100", "1000", "1000", "1110", "1100",
    #                          "1000", "1110", "1110", "1110"]

    print(dp_algorithm(sample_switch_bitmaps, 4))

    print(len(sample_switch_bitmaps))
