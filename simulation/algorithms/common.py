from simulation.utils import popcount
from functools import reduce
import random


# Note: Minimum-K-Union algorithm is adapted from
# https://stackoverflow.com/questions/12424155/given-n-sets-of-elements-find-minimal-union-of-m-sets


def min_k_union(nodes_map, nodes, k):
    min_k_bitmap = 0
    min_k_nodes = []
    for _ in range(k):
        node = min(nodes, key=lambda l: popcount(nodes_map[l]['bitmap'] | min_k_bitmap))
        nodes.remove(node)
        min_k_bitmap |= nodes_map[node]['bitmap']
        min_k_nodes += [node]
    return min_k_bitmap, min_k_nodes


def min_k_union_random(nodes_map, nodes, k, probability):
    min_k_bitmap = 0
    min_k_nodes = []
    for _ in range(k):
        temp_nodes = nodes[:]
        while True:
            if temp_nodes:
                node = min(temp_nodes, key=lambda l: popcount(nodes_map[l]['bitmap'] | min_k_bitmap))
                if random.random() < probability:
                    break
                temp_nodes.remove(node)
            else:
                break
        nodes.remove(node)
        min_k_bitmap |= nodes_map[node]['bitmap']
        min_k_nodes += [node]
    return min_k_bitmap, min_k_nodes


# Note: Set-Cover algorithm is adapted from
# http://www.martinbroadhurst.com/greedy-set-cover-in-python.html


def set_cover(bitmap, submaps):
    if reduce(lambda x, y: x | y, submaps) != bitmap:
        return None
    set_cover_bitmap = 0
    set_cover_submaps = []
    while set_cover_bitmap != bitmap:
        submap = max(submaps, key=lambda s: popcount(s & (~set_cover_bitmap)))
        submaps.remove(submap)
        set_cover_bitmap |= submap
        set_cover_submaps += [submap]
    return set_cover_submaps


def set_cover_random(bitmap, submaps, probability):
    if reduce(lambda x, y: x | y, submaps) != bitmap:
        return None
    set_cover_bitmap = 0
    set_cover_submaps = []
    while set_cover_bitmap != bitmap:
        temp_submaps = submaps[:]
        while True:
            if temp_submaps:
                submap = max(temp_submaps, key=lambda s: popcount(s & (~set_cover_bitmap)))
                if random.random() < probability:
                    break
                temp_submaps.remove(submap)
            else:
                break
        submaps.remove(submap)
        set_cover_bitmap |= submap
        set_cover_submaps += [submap]
    return set_cover_submaps


if __name__ == '__main__':
    bitmap = int('0b01101101', 2)
    submaps = [int('0b11110000', 2),
               int('0b00001111', 2),
               int('0b01001011', 2)]
    submaps = [submap & bitmap for submap in submaps]

    cover = set_cover(bitmap, submaps)
    print(cover)

    bitmap = int('0b01101101', 2)
    submaps = [int('0b11110000', 2),
               int('0b00001111', 2),
               int('0b01001011', 2)]
    submaps = [submap & bitmap for submap in submaps]

    random.seed(100)

    cover = set_cover_random(bitmap, submaps, 1/3*1.0)
    print(cover)
