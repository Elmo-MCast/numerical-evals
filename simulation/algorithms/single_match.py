from simulation.algorithms.common import min_k_union


def run(nodes_map, max_bitmaps, rules_count_map, max_rules):
    if len(nodes_map) <= max_bitmaps:
        return

    # Sort nodes based on their flow table size (descending order)
    ordered_nodes_list = sorted(nodes_map.items(), key=lambda item: rules_count_map[item[0]], reverse=True)

    # Find out the no. of nodes who have used up all their flow table space
    num_nodes_with_no_space = sum(1 for (n, _) in ordered_nodes_list if rules_count_map[n] >= max_rules)

    # If no. of nodes with no space is less than or equal to the no. of available bitmaps then assign them a bitmap ...
    if (num_nodes_with_no_space - max_bitmaps) <= 0:
        for i in range(max_bitmaps):
            n, _ = ordered_nodes_list[i]
            node = nodes_map[n]
            node['has_bitmap'] = i

        for i in range(max_bitmaps, len(nodes_map)):
            n, _ = ordered_nodes_list[i]
            node = nodes_map[n]
            node['has_rule'] = True
            rules_count_map[n] += 1

    # If no. of nodes with no space is greater than the no. of available bitmaps then assign them a bitmap and
    # rest the default bitmap ...
    else:
        ordered_nodes_with_no_space = [n for n, _ in ordered_nodes_list[:num_nodes_with_no_space]]
        default_bitmap, default_nodes = min_k_union(nodes_map, ordered_nodes_with_no_space,
                                                    num_nodes_with_no_space - max_bitmaps)

        for i, n in enumerate(ordered_nodes_with_no_space):
            node = nodes_map[n]
            node['has_bitmap'] = i

        for n in default_nodes:
            node = nodes_map[n]
            node['~bitmap'] = default_bitmap ^ node['bitmap']

        for i in range(num_nodes_with_no_space, len(nodes_map)):
            n, _ = ordered_nodes_list[i]
            node = nodes_map[n]
            node['has_rule'] = True
            rules_count_map[n] += 1

        return default_bitmap
