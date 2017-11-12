import random
import copy
from simulation.algorithms import single_match, exact_match, fuzzy_match, random_fuzzy_match, greedy_match

random.seed(0)


def test1_data():
    max_bitmaps = 3
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

    single_data = copy.deepcopy(data)
    single_match.run(single_data[0], single_data[1], single_data[4], single_data[5])

    exact_data = copy.deepcopy(data)
    exact_match.run(exact_data[0], exact_data[1], exact_data[2], exact_data[4], exact_data[5], is_strict=False)

    greedy_data = copy.deepcopy(data)
    greedy_match.run(greedy_data[0], greedy_data[1], greedy_data[2], greedy_data[3], greedy_data[4],
                     greedy_data[5])

    fuzzy_data = copy.deepcopy(data)
    fuzzy_match.run(fuzzy_data[0], fuzzy_data[1], fuzzy_data[2], fuzzy_data[3], fuzzy_data[4],
                    fuzzy_data[5])

    random_fuzzy_data = copy.deepcopy(data)
    random_fuzzy_match.run(random_fuzzy_data[0], random_fuzzy_data[1], random_fuzzy_data[2], random_fuzzy_data[3],
                           random_fuzzy_data[4], random_fuzzy_data[5])

    pass


test1_run()
