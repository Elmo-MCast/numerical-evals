from simulation.utils import popcount


def min_k_union(leafs_map, leafs, k):
    min_k_bitmap = 0
    min_k_leafs = []
    for _ in range(k):
        leaf = min(leafs, key=lambda l: popcount(leafs_map[l]['bitmap'] | min_k_bitmap))
        leafs.remove(leaf)
        min_k_bitmap |= leafs_map[leaf]['bitmap']
        min_k_leafs += [leaf]
    return min_k_bitmap, min_k_leafs


def run(data, max_bitmaps, max_leafs_per_bitmap, redundancy_per_bitmap, leafs_to_rules_count_map,
        max_rules_per_leaf):
    leaf_count = data['leaf_count']
    if leaf_count <= max_bitmaps:
        return

    leafs_map = data['leafs_map']
    leafs = [l for l in leafs_map]

    # Get packing of leafs per bitmap
    num_excess_leafs = leaf_count % max_bitmaps
    # @lalith: what is an unpacked leaf?
    # @shahbaz: I have renamed unpacked to excess. These are the excess leafs, left after dividing the total number of
    # leafs, for the given group, by max number of bitmaps. For example, if we have 2 bitmaps and 5 leafs, the excess
    # leafs are then 1. What this indicates is that we can uniformly divide 4 leafs across 2 bitmaps (each having
    # int(5 / 2) = 2 leafs) except the excess leafs.

    # @lalith: what exactly is this block below trying to do? (27-30)
    # @shahbaz: this blocks computes the number of leafs to assign per bitmap.
    # @shahbaz: this line computes how many leafs can be assigned to a given bitmap without considering the
    # max_leafs_per_bitmap constraint. For example, using our previous example, the no. of leafs per bitmap is 3.
    num_leafs_per_bitmap = int(leaf_count / max_bitmaps) + (1 if num_excess_leafs > 0 else 0)
    # @shahbaz: next, this code block checks if the no. of leafs per bitmap (computed in the above line) are greater
    # than max leafs per bitmap, if so, it caps the no. of leafs per bitmap to the max value and sets excess leafs to 0.
    if num_leafs_per_bitmap > max_leafs_per_bitmap:
        num_leafs_per_bitmap = max_leafs_per_bitmap
        num_excess_leafs = 0

    # @shahbaz: in short, the above code block is giving us two values: (1) no. of leafs per bitmap to initialize 'k'
    # with and (2) the no. of excess leafs.

    # Assign leafs to bitmaps
    # @lalith: what is the difference between num_leafs_per_bitmap, _num_leafs_per_bitmap, and __num_leafs_per_bitmap?
    #          and what is the relation to num_unpacked_leafs?
    # @shahbaz: I have renamed _num_leafs_per_bitmap to num_leafs_per_bitmap (i.e., overwriting the original value) and
    # __num_leafs_per_bitmap to running_num_leafs_per_bitmap.
    num_leafs_per_bitmap = num_leafs_per_bitmap if num_excess_leafs == 0 else num_leafs_per_bitmap - 1
    # @shahbaz: num_leafs_per_bitmap, at this point, tells us the number of leafs that can be evenly assigned to each
    # bitmap (excluding the excess leafs). The running_num_leafs_per_bitmap is initialized with num_leafs_per_bitmap.
    # We then check if we have some excess leafs left, if so, we increment running_num_leafs_per_bitmap to try to
    # come up with a grouping covering an excess leaf. (78) checks if the grouping is found or not. (Note: this will only
    # be checked for first iteration of k). If a grouping is found, we decrement the excess leafs by 1.
    # @shahbaz: this is also to ensure that we never input a 'k' to the min-k-union algorithm which is greater
    # than the number of input leafs at that point. This will result in error/exception.
    for i in range(max_bitmaps):
        running_num_leafs_per_bitmap = num_leafs_per_bitmap
        if num_excess_leafs > 0:
            running_num_leafs_per_bitmap += 1

        for k in range(running_num_leafs_per_bitmap, 0, -1):
            min_k_bitmap, min_k_leafs = min_k_union(leafs_map, leafs, k)
            _redundancy = sum([popcount(min_k_bitmap ^ leafs_map[l]['bitmap']) for l in min_k_leafs])
            if _redundancy <= redundancy_per_bitmap:
                for l in min_k_leafs:
                    # @lalith: what is this block doing? (49-51) Is 51 removing leaf['bitmap'] from the default bitmap?
                    leaf = leafs_map[l]
                    leaf['has_bitmap'] = i
                    leaf['~bitmap'] = min_k_bitmap ^ leaf['bitmap']
                    # @shahbaz: this block is only storing information that I use later for analysis (i.e., which
                    # bitmap a leaf is assigned to (71), and which redundant ports were set for that leaf (72). It's
                    # not removing the leaf['bitmap'], just keeping a bitmap with redundant bits set, for that leaf. leaf['bitmap']
                    # contains the actual bits for the leaf, and leaf['~bitmap'] contains the redundant/unwanted bits.

                if k == running_num_leafs_per_bitmap and num_excess_leafs > 0:
                    num_excess_leafs -= 1
                break
            else:
                leafs += min_k_leafs

    # Add a rule or assign leafs to default bitmap
    default_bitmap = 0
    for l in leafs:
        leaf = leafs_map[l]
        if leafs_to_rules_count_map[l] < max_rules_per_leaf:  # Add a rule in leaf
            leaf['has_rule'] = True
            leafs_to_rules_count_map[l] += 1
        else:  # Assign leaf to default bitmap
            default_bitmap |= leaf['bitmap']

    # Calculate redundancy
    for l in leafs:
        leaf = leafs_map[l]
        if 'has_rule' not in leaf:
            leaf['~bitmap'] = default_bitmap ^ leaf['bitmap']

    data['default_bitmap'] = default_bitmap
