import numpy as np
import itertools


def min_k_union(leafs_map, leafs, num_hosts_per_leaf, k):
    _bitmap = np.array([0] * num_hosts_per_leaf)
    _leafs = []
    for _ in range(k):
        leaf = min(leafs, key=lambda l: np.count_nonzero(leafs_map[l]['bitmap'] | _bitmap))
        leafs.remove(leaf)
        _bitmap |= leafs_map[leaf]['bitmap']
        _leafs += [leaf]
    return _bitmap, _leafs


def run(data, max_bitmaps, max_leafs_per_bitmap, leafs_to_rules_count_map, max_rules_per_leaf, num_hosts_per_leaf):
    if data['leaf_count'] <= max_bitmaps:
        return

    leafs_map = data['leafs_map']

    leafs = [l for l in leafs_map]
    num_unpacked_leafs = data['leaf_count'] % max_bitmaps
    num_leafs_per_bitmap = int(data['leaf_count'] / max_bitmaps) + (1 if num_unpacked_leafs > 0 else 0)
    if num_leafs_per_bitmap > max_leafs_per_bitmap:
        num_leafs_per_bitmap = max_leafs_per_bitmap
        num_unpacked_leafs = 0

    # Assign leafs to bitmaps
    _num_leafs_per_bitmap = num_leafs_per_bitmap if num_unpacked_leafs == 0 else num_leafs_per_bitmap - 1
    for i in range(max_bitmaps):
        __num_leafs_per_bitmap = _num_leafs_per_bitmap
        if num_unpacked_leafs > 0:
            __num_leafs_per_bitmap += 1

        _bitmap, _leafs = min_k_union(leafs_map, leafs, num_hosts_per_leaf, __num_leafs_per_bitmap)

        for l in _leafs:
            leafs_map[l]['has_bitmap'] = True
            leafs_map[l]['has_rule'] = False
            leafs_map[l]['~bitmap'] = _bitmap ^ leafs_map[l]['bitmap']

        num_unpacked_leafs -= (__num_leafs_per_bitmap - _num_leafs_per_bitmap)

    # Initializing default bitmap
    data['default_bitmap'] = np.array([0] * num_hosts_per_leaf)

    # Add a rule or assign leafs to default bitmap
    for l in leafs:
        if leafs_to_rules_count_map[l] < max_rules_per_leaf:  # Add a rule in leaf
            leafs_map[l]['has_bitmap'] = False
            leafs_map[l]['has_rule'] = True
            leafs_to_rules_count_map[l] += 1
        else:  # Assign leaf to default bitmap
            leafs_map[l]['has_bitmap'] = False
            leafs_map[l]['has_rule'] = False
            data['default_bitmap'] |= leafs_map[l]['bitmap']

    # Calculate redundancy
    data['r'] = 0
    for l in leafs_map:
        if leafs_map[l]['has_bitmap']:
            data['r'] += np.count_nonzero(leafs_map[l]['~bitmap'])
        elif not leafs_map[l]['has_rule']:
            leafs_map[l]['~bitmap'] = data['default_bitmap'] ^ leafs_map[l]['bitmap']
            data['r'] += np.count_nonzero(leafs_map[l]['~bitmap'])
