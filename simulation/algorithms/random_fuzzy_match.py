import itertools
import random


def run(data, max_bitmaps, max_leafs_per_bitmap, leafs_to_rules_count_map, max_rules_per_leaf, num_hosts_per_leaf):
    if data['leaf_count'] <= max_bitmaps:
        return

    leafs_map = data['leafs_map']
    leafs = [l for l in leafs_map]

    # Generate combinations of leafs
    combinations = dict()
    num_unpacked_leafs = data['leaf_count'] % max_bitmaps
    num_combinations = int(data['leaf_count'] / max_bitmaps) + (1 if num_unpacked_leafs > 0 else 0)
    if num_combinations > max_leafs_per_bitmap:
        num_combinations = max_leafs_per_bitmap
        num_unpacked_leafs = 0
    for i in range(1, num_combinations + 1):
        combinations[i] = dict()
        for c in itertools.combinations(leafs, i):
            if i == 1:
                combinations[i][c] = (leafs_map[c[0]]['bitmap'], 0)
            else:
                combinations[i][c] = (
                    combinations[i - 1][c[:len(c) - 1]][0] | leafs_map[c[len(c) - 1]]['bitmap'],
                    combinations[i - 1][c[:len(c) - 1]][1] +
                    bin(combinations[i - 1][c[:len(c) - 1]][0] ^ leafs_map[c[len(c) - 1]]['bitmap'])[2:].count('1'))

    # Sort combinations of leafs based on their hamming distance value
    sorted_combinations = dict()
    for i in range(1, num_combinations + 1):
        sorted_combinations[i] = sorted(combinations[i].items(),
                                        key=lambda item: item[1][1])

        # Dropping the first combination with 1/3 probability
        if i > 1 and random.randint(0, 2) == 0:
            sorted_combinations[i].remove(sorted_combinations[i][0])

    # Assign leafs to bitmaps using the sorted combinations of leafs
    seen_leafs = set()
    _num_combinations = num_combinations if num_unpacked_leafs == 0 else num_combinations - 1
    for i in range(max_bitmaps):
        num_combination = _num_combinations
        if num_unpacked_leafs > 0:
            num_combination += 1
            num_unpacked_leafs -= 1

        while True:
            if sorted_combinations[num_combination]:
                selected_combination = sorted_combinations[num_combination][0]
                if len(set(selected_combination[0]) - seen_leafs) != len(selected_combination[0]):
                    sorted_combinations[num_combination].remove(selected_combination)
                    continue

                for l in selected_combination[0]:
                    leafs_map[l]['has_bitmap'] = True
                    leafs_map[l]['has_rule'] = False
                    leafs_map[l]['~bitmap'] = selected_combination[1][0] ^ leafs_map[l]['bitmap']

                seen_leafs |= set(selected_combination[0])
                sorted_combinations[num_combination].remove(selected_combination)
                break
            else:
                num_combination -= 1

    remaining_leafs = set(leafs) - seen_leafs

    # Initializing default bitmap
    data['default_bitmap'] = 0

    # Add a rule or assign leafs to default bitmap
    for l in remaining_leafs:
        if leafs_to_rules_count_map[l] < max_rules_per_leaf:  # Add a rule in leaf
            leafs_map[l]['has_bitmap'] = False
            leafs_map[l]['has_rule'] = True
            leafs_to_rules_count_map[l] += 1
        else:  # Assign leaf to default bitmap
            leafs_map[l]['has_bitmap'] = False
            leafs_map[l]['has_rule'] = False
            data['default_bitmap'] |= leafs_map[l]['bitmap']

    for l in remaining_leafs:
        if not leafs_map[l]['has_rule']:
            leafs_map[l]['~bitmap'] = data['default_bitmap'] ^ leafs_map[l]['bitmap']
