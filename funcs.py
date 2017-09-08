
def organize_bitmaps(input_bitmaps):
    "reorder the bits to follow the algorithm assumptions"
    if (input_bitmaps == []):
        return
    Q = len(input_bitmaps)
    W = len(input_bitmaps[0])
    cnt = [len([j for j in range(Q) if input_bitmaps[j][i] == "1"])  for i in range(W)]

    perm = []
    while (len(perm) < W):
        max_cnt = 0
        for i in range(W):
            if cnt[i] > max_cnt:
                ind = i
                max_cnt = cnt[i]
        nax_cnt = 0
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

def ones(str):
    "counts the number of ones in a string"
    c = len([x for x in str if x == "1"])
    return c

def DP_ALGO(switch_bitmaps, num_group_bitmaps):
    "Find groups serving the demands of switch_bitmaps with a minimal redundant traffic"
    G = num_group_bitmaps
    Q = len(switch_bitmaps)
    W = len(switch_bitmaps[0])
    bitmaps, perm = organize_bitmaps(switch_bitmaps)
    bitmaps_num = [ones(bitmap) for bitmap in bitmaps]
    # print bitmaps_num, bitmaps
    print(bitmaps)
    max_demand = Q * W * 2
    # print "max:", max_demand
    R = [[max_demand for g in range( G +1)] for q in range( Q +1)]
    Y = [[[] for g in range( G +1)] for q in range( Q +1)]

    for g in range(0 , G +1):
        R[0][g] = 0
        Y[0][g] = []
    for g in range(1 , G +1):
        R[1][g] = 0
        Y[1][g] = [1]
    # print Y
    # print
    for q in range(2 , Q +1):
        # serving the first q masks
        for g in range(1 , G +1):
            # using at most g masks
            r = max_demand
            if (R[q][ g -1] == 0):
                R[q][g] = 0
                Y[q][g] = Y[q][ g -1] + [0]
                continue
            for j in range(1 , q +1):
                r = R[ q -j][ g -1]
                # print "!", q, g, r, "  ", "(", q-j, g-1, ")",
                r += sum([bitmaps_num[ q -1] - bitmaps_num[q - k] for k in range(1 , j +1)])
                # print r
                if (r <= R[q][g]):
                    R[q][g] = r
                    Y[q][g] = Y[ q -j][ g -1] + [j]
                    # print q, R[:q+1]
                    # print q, Y[:q+1]
                    # print
                    # print

    group_bitmaps = []
    c = 0
    for g in range(G):
        # print "#", len(Y), len(Y[Q]), len(Y[Q][G]), Q, G, g, Y[Q][G]
        c += Y[Q][G][g]
        group_bitmaps.append(bitmaps[ c -1])

    switch_to_group_map = [-1 for q in range(Q)]
    c = 0
    for g in range(1 , G +1):
        for x in range(c, c + Y[Q][G][ g -1]):
            switch_to_group_map[x] = g
        c += Y[Q][G][ g -1]
    r = R[Q][G]
    min_no_redundancy = -1
    if (r == 0):
        min_no_redundancy = max(switch_to_group_map)
    return (group_bitmaps, switch_to_group_map, r ,min_no_redundancy)

# switch_bitmaps = ["1000","1100","1000","1000","1111", "1110","1100","1111","1000","1111","1110","1110","1110"]

if __name__ == "__main__":
    sample_switch_bitmaps = ["1000", "1100", "1000", "1000", "1111", "1110", "1100",
                             "1111", "1000", "1111", "1110", "1110", "1110"]

    # sample_switch_bitmaps = ["1000", "1100", "1000", "1000", "1110", "1100",
    #                          "1000", "1110", "1110", "1110"]

    print(DP_ALGO(sample_switch_bitmaps, 10))

    print(len(sample_switch_bitmaps))

