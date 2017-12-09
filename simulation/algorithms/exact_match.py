def run(nodes_map, max_bitmaps, max_nodes_per_bitmap, rules_count_map, max_rules):
    if len(nodes_map) <= max_bitmaps:
        return

    # Generating bitmap-to-nodes mapping
    bitmap_to_nodes_map = dict()
    for n in nodes_map:
        bitmap = nodes_map[n]['bitmap']
        if bitmap in bitmap_to_nodes_map:
            bitmap_to_nodes_map[bitmap] += [n]
        else:
            bitmap_to_nodes_map[bitmap] = [n]

    # Sorting bitmap-to-nodes mapping based on the number of nodes per bitmap (descending order)
    ordered_bitmap_list = sorted(bitmap_to_nodes_map.items(), key=lambda item: len(item[1]), reverse=True)

    # Assigning nodes to bitmaps, rules, and default bitmap
    num_nodes_covered_with_bitmaps = max_bitmaps * max_nodes_per_bitmap
    num_bitmaps = 0
    default_bitmap = 0
    for _, nodes in ordered_bitmap_list:
        while nodes:
            num_nodes_per_bitmap = min(num_nodes_covered_with_bitmaps, len(nodes))

            if num_nodes_per_bitmap > 0 and num_bitmaps < max_bitmaps:
                for n in nodes[:num_nodes_per_bitmap]:
                    node = nodes_map[n]
                    node['has_bitmap'] = num_bitmaps
                nodes = nodes[num_nodes_per_bitmap:]
                num_nodes_covered_with_bitmaps -= num_nodes_per_bitmap
                num_bitmaps += 1
            else:
                for n in nodes:
                    node = nodes_map[n]
                    if rules_count_map[n] < max_rules:
                        node['has_rule'] = True
                        rules_count_map[n] += 1
                    else:
                        default_bitmap |= node['bitmap']
                nodes = []

    # Calculate redundancy for leafs assigned to default bitmap
    for n in nodes_map:
        node = nodes_map[n]
        if 'has_bitmap' not in node and 'has_rule' not in node:
            node['~bitmap'] = default_bitmap ^ node['bitmap']

    return default_bitmap
