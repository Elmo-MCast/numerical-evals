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


if __name__ == "__main__":
    # sample_switch_bitmaps = ["1000", "1100", "1000", "1000", "1111", "1110", "1100",
    #                          "1111", "1000", "1111", "1110", "1110", "1110"]

    # sample_switch_bitmaps = ["1000", "1100", "1000", "1000", "1110", "1100",
    #                          "1000", "1110", "1110", "1110"]

    sample_switch_bitmaps = {
        1: BitArray('0b1000'),
        2: BitArray('0b1100'),
        3: BitArray('0b1000'),
        4: BitArray('0b1000'),
        5: BitArray('0b1111'),
        6: BitArray('0b1110'),
        7: BitArray('0b1100'),
        8: BitArray('0b1111'),
        9: BitArray('0b1000'),
        10: BitArray('0b1111'),
        11: BitArray('0b1110'),
        12: BitArray('0b1110'),
        13: BitArray('0b1110')
    }

    print(organize_bitmaps(sample_switch_bitmaps))