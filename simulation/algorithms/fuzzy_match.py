from bitstring import BitArray
import itertools
import functools


def run(data, max_bitmaps, max_leafs_per_bitmap, leafs_to_rules_count_map, max_rules_per_leaf, num_hosts_per_leaf):
    if data['leaf_count'] <= max_bitmaps:
        return

    if data['leaf_count'] >= 12:
        pass


    leafs_map = data['leafs_map']
    leafs = [l for l in leafs_map]

    combinations = dict()
    remaining_leafs = data['leaf_count'] % max_bitmaps
    num_combinations = int(data['leaf_count'] / max_bitmaps) + (1 if remaining_leafs > 0 else 0)
    if num_combinations > max_leafs_per_bitmap:
        num_combinations = max_leafs_per_bitmap

    for i in range(1, num_combinations + 1):
        combinations[i] = dict()
        for c in itertools.combinations(range(data['leaf_count']), i):
            if i == 1:
                combinations[i][c] = (leafs_map[leafs[c[0]]]['bitmap'], 0)
            else:
                combinations[i][c] = (
                    combinations[i - 1][c[:len(c) - 1]][0] | leafs_map[leafs[c[len(c) - 1]]]['bitmap'],
                    combinations[i - 1][c[:len(c) - 1]][1] +
                    sum(combinations[i - 1][c[:len(c) - 1]][0] ^ leafs_map[leafs[c[len(c) - 1]]]['bitmap']))

    sorted_combinations = dict()
    for i in range(1, num_combinations + 1):
        sorted_combinations[i] = sorted(combinations[i].items(),
                                        key=lambda item: item[1][1])

    seen_combinations = set()
    _num_combinations = num_combinations if remaining_leafs == 0 else num_combinations - 1
    for i in range(max_bitmaps):
        num_combination = _num_combinations
        if remaining_leafs > 0:
            num_combination += 1

        while True:
            selected_combination = sorted_combinations[num_combination][0]

            if len(set(selected_combination[0]) - seen_combinations) != len(selected_combination[0]):
                sorted_combinations[num_combination].remove(selected_combination)
                continue

            for c in selected_combination[0]:
                leafs_map[leafs[c]]['has_bitmap'] = True
                leafs_map[leafs[c]]['has_rule'] = False
                leafs_map[leafs[c]]['~bitmap'] = selected_combination[1][0] ^ leafs_map[leafs[c]]['bitmap']

            seen_combinations |= set(selected_combination[0])
            sorted_combinations[num_combination].remove(selected_combination)
            break

        remaining_leafs -= (num_combination - _num_combinations)

    pass
