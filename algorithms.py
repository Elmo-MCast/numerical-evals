from bitstring import BitArray


# Collection of Algorithms


# 1. Dummy

def dummy(leaf_bitmaps, num_bitmaps):
    return ([BitArray(len(leaf_bitmaps[list(leaf_bitmaps.keys())[0]]))] * num_bitmaps,
            {i: i for i in range(num_bitmaps)}, 10, len(leaf_bitmaps))


# 2. Dynamic Programming

def ones(bitmap):
    """counts the number of ones in a bitmap"""
    count = len([bit for bit in bitmap if bit == 1])
    return count


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

if __name__ == "__main__":
    sample_switch_bitmaps = ["1000", "1100", "1000", "1000", "1111", "1110", "1100",
                             "1111", "1000", "1111", "1110", "1110", "1110"]

    # sample_switch_bitmaps = ["1000", "1100", "1000", "1000", "1110", "1100",
    #                          "1000", "1110", "1110", "1110"]

    print(organize_bitmaps(sample_switch_bitmaps))