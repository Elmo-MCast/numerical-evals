from simulation.utils import popcount
from timeit import default_timer as timer
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

    good_leafs = [l for l in leafs]
    good_combination = [([l], (leafs_map[l]['bitmap'], 0)) for l in good_leafs]
    combinations[0] = good_combination

    for i in range(1, num_leafs_per_bitmap):
        combination = []
        for c, (b, _) in good_combination:
            for l in good_leafs:
                if l not in c:
                    _c = c + [l]
                    _b = b | leafs_map[l]['bitmap']
                    _r = sum([popcount(_b ^ leafs_map[_l]['bitmap']) for _l in _c])

                    if _r <= redundancy_per_bitmap:
                        combination += [(_c, (_b, _r))]

        if combination:
            good_leafs = list(set([y for x in combination for y in x[0]]))
            good_combination = combination
        else:
            break

    for i in range(1, num_leafs_per_bitmap):
        if combinations[i]:
            combinations[i] = sorted(combinations[i], key=lambda item: item[1][1])
            if random.randint(0, 2) == 0:
                combinations[i] = combinations[i][1:]

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
                    combinations[__num_leafs_per_bitmap - 1] = combination[1:]
                    continue

                for l in c:
                    leaf = leafs_map[l]
                    leaf['has_bitmap'] = True
                    leaf['has_rule'] = False
                    leaf['~bitmap'] = b ^ leaf['bitmap']

                seen_leafs |= set(c)
                combinations[__num_leafs_per_bitmap - 1] = combination[1:]
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
