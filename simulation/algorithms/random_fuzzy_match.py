import itertools
import random


def run(data, max_bitmaps, max_leafs_per_bitmap, redundancy_per_bitmap, leafs_to_rules_count_map, max_rules_per_leaf):
    leaf_count = data['leaf_count']
    if leaf_count <= max_bitmaps:
        return

    leafs_map = data['leafs_map']
    leafs = [l for l in leafs_map]

    # Generate combinations of leafs
    num_unpacked_leafs = leaf_count % max_bitmaps
    num_leafs_per_bitmap = int(leaf_count / max_bitmaps) + (1 if num_unpacked_leafs > 0 else 0)
    if num_leafs_per_bitmap > max_leafs_per_bitmap:
        num_leafs_per_bitmap = max_leafs_per_bitmap
        num_unpacked_leafs = 0
    combinations = [None] * num_leafs_per_bitmap

    combination = dict()
    for c in itertools.combinations(leafs, 1):
        combination[c] = (leafs_map[c[0]]['bitmap'], 0)
    previous_combination = combination
    combinations[0] = list(combination.items())

    for i in range(1, num_leafs_per_bitmap):
        combination = dict()
        for c in itertools.combinations(leafs, i + 1):
            previous_c = c[:i]
            if previous_c in previous_combination:
                _bitmap = previous_combination[previous_c][0] | leafs_map[c[i]]['bitmap']
                _redundancy = sum([bin(_bitmap ^ leafs_map[l]['bitmap'])[2:].count('1') for l in c])
                combination[c] = (_bitmap, _redundancy)

        combination = sorted(combination.items(), key=lambda item: item[1][1])
        j = next((x for x, y in enumerate(combination) if y[1][1] >= redundancy_per_bitmap), None)
        if j is not None:
            del combination[j:len(combination)]

        if combination:
            if random.randint(0, 2) == 0:
                combination.remove(combination[0])
            if combination:
                previous_combination = dict(combination)
                combinations[i] = combination
            else:
                break
        else:
            break

    # Assign leafs to bitmaps using the sorted combinations of leafs
    seen_leafs = set()
    _num_leafs_per_bitmap = num_leafs_per_bitmap if num_unpacked_leafs == 0 else num_leafs_per_bitmap - 1
    for i in range(max_bitmaps):
        __num_leafs_per_bitmap = _num_leafs_per_bitmap
        if num_unpacked_leafs > 0:
            __num_leafs_per_bitmap += 1

        while True:
            combination = combinations[__num_leafs_per_bitmap - 1]
            if combination:
                current_item = combination[0]
                c, b = current_item[0], current_item[1][0]
                if len(set(c) - seen_leafs) != len(c):
                    combination.remove(current_item)
                    continue

                for l in c:
                    leaf = leafs_map[l]
                    leaf['has_bitmap'] = True
                    leaf['has_rule'] = False
                    leaf['~bitmap'] = b ^ leaf['bitmap']

                seen_leafs |= set(c)
                combination.remove(current_item)
                break
            else:
                __num_leafs_per_bitmap -= 1

        if __num_leafs_per_bitmap <= _num_leafs_per_bitmap:
            _num_leafs_per_bitmap = __num_leafs_per_bitmap
            num_unpacked_leafs = 0
        else:
            num_unpacked_leafs -= 1

    remaining_leafs = set(leafs) - seen_leafs

    # Add a rule or assign leafs to default bitmap
    default_bitmap = 0
    for l in remaining_leafs:
        leaf = leafs_map[l]
        if leafs_to_rules_count_map[l] < max_rules_per_leaf:  # Add a rule in leaf
            leaf['has_bitmap'] = False
            leaf['has_rule'] = True
            leafs_to_rules_count_map[l] += 1
        else:  # Assign leaf to default bitmap
            leaf['has_bitmap'] = False
            leaf['has_rule'] = False
            default_bitmap |= leaf['bitmap']

    for l in remaining_leafs:
        leaf = leafs_map[l]
        if not leaf['has_rule']:
            leaf['~bitmap'] = default_bitmap ^ leaf['bitmap']

    data['default_bitmap'] = default_bitmap
