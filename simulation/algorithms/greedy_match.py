from simulation.utils import popcount


def min_k_union(leafs_map, leafs, k):
    _bitmap = 0
    _leafs = []
    for _ in range(k):
        leaf = min(leafs, key=lambda l: popcount(leafs_map[l]['bitmap'] | _bitmap))
        leafs.remove(leaf)
        _bitmap |= leafs_map[leaf]['bitmap']
        _leafs += [leaf]
    return _bitmap, _leafs


def run(data, max_bitmaps, max_leafs_per_bitmap, redundancy_per_bitmap, leafs_to_rules_count_map,
        max_rules_per_leaf):
    leaf_count = data['leaf_count']
    if leaf_count <= max_bitmaps:
        return

    leafs_map = data['leafs_map']
    leafs = [l for l in leafs_map]

    # Get packing of leafs per bitmap
    num_unpacked_leafs = leaf_count % max_bitmaps
    num_leafs_per_bitmap = int(leaf_count / max_bitmaps) + (1 if num_unpacked_leafs > 0 else 0)
    if num_leafs_per_bitmap > max_leafs_per_bitmap:
        num_leafs_per_bitmap = max_leafs_per_bitmap
        num_unpacked_leafs = 0

    # Assign leafs to bitmaps
    _num_leafs_per_bitmap = num_leafs_per_bitmap if num_unpacked_leafs == 0 else num_leafs_per_bitmap - 1
    for i in range(max_bitmaps):
        __num_leafs_per_bitmap = _num_leafs_per_bitmap
        if num_unpacked_leafs > 0:
            __num_leafs_per_bitmap += 1

        for j in range(__num_leafs_per_bitmap, 0, -1):
            _bitmap, _leafs = min_k_union(leafs_map, leafs, j)
            _redundancy = sum([popcount(_bitmap ^ leafs_map[l]['bitmap']) for l in _leafs])
            if _redundancy <= redundancy_per_bitmap:
                for l in _leafs:
                    leaf = leafs_map[l]
                    leaf['has_bitmap'] = True
                    leaf['has_rule'] = False
                    leaf['~bitmap'] = _bitmap ^ leaf['bitmap']

                if j == __num_leafs_per_bitmap and num_unpacked_leafs > 0:
                    num_unpacked_leafs -= 1
                break
            else:
                leafs += _leafs

    # Add a rule or assign leafs to default bitmap
    default_bitmap = 0
    for l in leafs:
        leaf = leafs_map[l]
        if leafs_to_rules_count_map[l] < max_rules_per_leaf:  # Add a rule in leaf
            leaf['has_bitmap'] = False
            leaf['has_rule'] = True
            leafs_to_rules_count_map[l] += 1
        else:  # Assign leaf to default bitmap
            leaf['has_bitmap'] = False
            leaf['has_rule'] = False
            default_bitmap |= leaf['bitmap']

    # Calculate redundancy
    for l in leafs:
        leaf = leafs_map[l]
        if not leaf['has_rule']:
            leaf['~bitmap'] = default_bitmap ^ leaf['bitmap']

    data['default_bitmap'] = default_bitmap
