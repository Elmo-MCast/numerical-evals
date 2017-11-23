from simulation.utils import popcount
import random


def min_k_union(leafs_map, leafs, k):
    min_k_bitmap = 0
    min_k_leafs = []
    for _ in range(k):
        leaf = min(leafs, key=lambda l: popcount(leafs_map[l]['bitmap'] | min_k_bitmap))
        leafs.remove(leaf)
        min_k_bitmap |= leafs_map[leaf]['bitmap']
        min_k_leafs += [leaf]
    return min_k_bitmap, min_k_leafs


def min_k_union_random(leafs_map, leafs, k, probability):
    min_k_bitmap = 0
    min_k_leafs = []
    for _ in range(k):
        temp_leafs = leafs[:]
        while True:
            if temp_leafs:
                leaf = min(temp_leafs, key=lambda l: popcount(leafs_map[l]['bitmap'] | min_k_bitmap))
                if random.random() < probability:
                    break
                temp_leafs.remove(leaf)
            else:
                break
        leafs.remove(leaf)
        min_k_bitmap |= leafs_map[leaf]['bitmap']
        min_k_leafs += [leaf]
    return min_k_bitmap, min_k_leafs
