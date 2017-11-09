import random
from simulation.algorithms import single_match, exact_match, fuzzy_match

random.seed(0)


def test1_data():
    max_bitmaps = 5
    max_leafs_per_bitmap = 1
    num_leafs = 64
    leafs_to_rules_count = [0] * num_leafs
    max_rules_per_leaf = 1

    leaf_count = 5
    leafs = {0, 10, 20, 30, 40}
    leafs_map = dict()
    for i, l in enumerate(leafs):
        leafs_map[l] = {'bitmap': i}

    data = {
        'leaf_count': leaf_count,
        'leafs_map': leafs_map
    }

    return data, max_bitmaps, max_leafs_per_bitmap, leafs_to_rules_count, max_rules_per_leaf


def test1_run():
    (data, max_bitmaps, max_leafs_per_bitmap,
     leafs_to_rules_count, max_rules_per_leaf) = test1_data()
    single_match.run(data, max_bitmaps, leafs_to_rules_count, max_rules_per_leaf)
    assert sum(leafs_to_rules_count) == 0
    for l in data['leafs_map']:
        assert 'has_bitmap' not in data['leafs_map'][l]
        assert 'has_rule' not in data['leafs_map'][l]
        assert '~bitmap' not in data['leafs_map'][l]
    assert 'default_bitmap' not in data['leafs_map']

    (data, max_bitmaps, max_leafs_per_bitmap,
     leafs_to_rules_count, max_rules_per_leaf) = test1_data()
    exact_match.run(data, max_bitmaps, max_leafs_per_bitmap, leafs_to_rules_count, max_rules_per_leaf)
    assert sum(leafs_to_rules_count) == 0
    for l in data['leafs_map']:
        assert 'has_bitmap' not in data['leafs_map'][l]
        assert 'has_rule' not in data['leafs_map'][l]
        assert '~bitmap' not in data['leafs_map'][l]
    assert 'default_bitmap' not in data['leafs_map']


def test2_data():
    max_bitmaps = 2
    max_leafs_per_bitmap = 2
    redundancy_per_bitmap = 0
    num_leafs = 64
    leafs_to_rules_count = [0] * num_leafs
    max_rules_per_leaf = 1

    leaf_count = 5
    leafs = {0, 10, 20, 30, 40}
    leafs_map = dict()
    for i, l in enumerate(leafs):
        if i < 4:
            leafs_map[l] = {'bitmap': 1}
        else:
            leafs_map[l] = {'bitmap': 10}

    data = {
        'leaf_count': leaf_count,
        'leafs_map': leafs_map
    }

    return data, max_bitmaps, max_leafs_per_bitmap, redundancy_per_bitmap, leafs_to_rules_count, max_rules_per_leaf


def test2_run():
    (data0, max_bitmaps0, max_leafs_per_bitmap0, _,
     leafs_to_rules_count0, max_rules_per_leaf0) = test2_data()
    exact_match.run(data0, max_bitmaps0, max_leafs_per_bitmap0, leafs_to_rules_count0, max_rules_per_leaf0)

    (data1, max_bitmaps1, max_leafs_per_bitmap1, redundancy_per_bitmap1,
     leafs_to_rules_count1, max_rules_per_leaf1) = test2_data()
    fuzzy_match.run(data1, max_bitmaps1, max_leafs_per_bitmap1, redundancy_per_bitmap1, leafs_to_rules_count1,
                    max_rules_per_leaf1)
    pass


test2_run()
