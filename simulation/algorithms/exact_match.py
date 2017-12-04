def run(group, max_bitmaps, max_leafs_per_bitmap, leafs_to_rules_count_map, max_rules_per_leaf):
    leafs_map = group['leafs_map']
    if len(leafs_map) <= max_bitmaps:
        return

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
    num_leafs_covered_with_bitmaps = max_bitmaps * max_leafs_per_bitmap
    num_bitmaps = 0
    default_bitmap = 0
    for _, leafs in ordered_bitmap_list:
        while leafs:
            num_leafs_per_bitmap = min(num_leafs_covered_with_bitmaps, len(leafs))

            if num_leafs_per_bitmap > 0 and num_bitmaps < max_bitmaps:
                for l in leafs[:num_leafs_per_bitmap]:
                    leaf = leafs_map[l]
                    leaf['has_bitmap'] = num_bitmaps
                leafs = leafs[num_leafs_per_bitmap:]
                num_leafs_covered_with_bitmaps -= num_leafs_per_bitmap
                num_bitmaps += 1
            else:
                for l in leafs:
                    leaf = leafs_map[l]
                    if leafs_to_rules_count_map[l] < max_rules_per_leaf:
                        leaf['has_rule'] = True
                        leafs_to_rules_count_map[l] += 1
                    else:
                        default_bitmap |= leaf['bitmap']
                leafs = []

    # Calculate redundancy for leafs assigned to default bitmap
    for l in leafs_map:
        leaf = leafs_map[l]
        if 'has_bitmap' not in leaf and 'has_rule' not in leaf:
            leaf['~bitmap'] = default_bitmap ^ leaf['bitmap']

    group['default_bitmap'] = default_bitmap
