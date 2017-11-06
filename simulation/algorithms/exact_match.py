def run(data, max_bitmaps, max_leafs_per_bitmap, leafs_to_rules_count_map, max_rules_per_leaf):
    leaf_count = data['leaf_count']
    if leaf_count <= max_bitmaps:
        return

    leafs_map = data['leafs_map']

    # Generating bitmaps-to-leaf mapping
    bitmap_to_leafs_map = dict()
    for l in leafs_map:
        bitmap = leafs_map[l]['bitmap']
        if bitmap in bitmap_to_leafs_map:
            bitmap_to_leafs_map[bitmap] += [l]
        else:
            bitmap_to_leafs_map[bitmap] = [l]

    # Sorting bitmaps-to-leaf mapping based on the number of leafs per bitmap (descending order)
    ordered_bitmap_list = sorted(bitmap_to_leafs_map.items(), key=lambda item: len(item[1]), reverse=True)

    # Assigning leafs to bitmaps, rules, and default bitmap
    bitmap_count = 0
    leafs_per_bitmap_count = 0
    leafs_budget_count = (max_bitmaps * max_leafs_per_bitmap) - max_bitmaps
    default_bitmap = 0
    for _, leafs in ordered_bitmap_list:
        for l in leafs:
            leaf = leafs_map[l]
            if bitmap_count < max_bitmaps:  # Assign leaf to a bitmap
                leaf['has_bitmap'] = True
                leaf['has_rule'] = False
                leafs_per_bitmap_count += 1

                # Select next bitmap, when no. of leafs assigned is equal to (1 + leafs_budget_count)
                if leafs_per_bitmap_count == (1 + leafs_budget_count):
                    leafs_budget_count = 0
                    bitmap_count += 1
                    leafs_per_bitmap_count = 0
            else:
                if leafs_to_rules_count_map[l] < max_rules_per_leaf:  # Add a rule in leaf
                    leaf['has_bitmap'] = False
                    leaf['has_rule'] = True
                    leafs_to_rules_count_map[l] += 1
                else:  # Assign leaf to default bitmap
                    leaf['has_bitmap'] = False
                    leaf['has_rule'] = False
                    default_bitmap |= leaf['bitmap']

        # Select next bitmap, if the current bitmap contains any leaf
        if bitmap_count < max_bitmaps and leafs_per_bitmap_count > 0:
            leafs_budget_count -= (leafs_per_bitmap_count - 1)
            bitmap_count += 1
            leafs_per_bitmap_count = 0

    for l in leafs_map:
        leaf = leafs_map[l]
        if not (leaf['has_bitmap'] or leaf['has_rule']):
            leaf['~bitmap'] = default_bitmap ^ leaf['bitmap']

    data['default_bitmap'] = default_bitmap
