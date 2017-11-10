import random
import copy
from simulation.algorithms import single_match, exact_match, fuzzy_match

random.seed(0)


def test1_data():
    max_bitmaps = 2
    max_leafs_per_bitmap = 2
    redundancy_per_bitmap = 0
    num_leafs = 576
    leafs_to_rules_count = [0] * num_leafs
    max_rules_per_leaf = 0

    leaf_count = 5
    leafs = [i for i in range(leaf_count)]
    leafs_map = dict()
    for i, l in enumerate(leafs):
        # leafs_map[l] = {'bitmap': random.randint(0, num_leafs)}
        if i < 3:
            leafs_map[l] = {'bitmap': 1}
        else:
            leafs_map[l] = {'bitmap': i}

    data = {
        'leaf_count': leaf_count,
        'leafs_map': leafs_map
    }

    return data, max_bitmaps, max_leafs_per_bitmap, redundancy_per_bitmap, leafs_to_rules_count, max_rules_per_leaf


def test1_run():
    data = test1_data()

    (data0, max_bitmaps0, max_leafs_per_bitmap0, _,
     leafs_to_rules_count0, max_rules_per_leaf0) = copy.deepcopy(data)
    exact_match.run(data0, max_bitmaps0, max_leafs_per_bitmap0, leafs_to_rules_count0, max_rules_per_leaf0)

    (data1, max_bitmaps1, max_leafs_per_bitmap1, redundancy_per_bitmap1,
     leafs_to_rules_count1, max_rules_per_leaf1) = copy.deepcopy(data)
    fuzzy_match.run(data1, max_bitmaps1, max_leafs_per_bitmap1, redundancy_per_bitmap1, leafs_to_rules_count1,
                    max_rules_per_leaf1)
    pass


test1_run()
