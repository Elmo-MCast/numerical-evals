from math import ceil
from simulation.utils import popcount
from simulation.algorithms.common import min_k_union_random as min_k_union


def run(nodes_map, max_bitmaps, max_nodes_per_bitmap, redundancy_per_bitmap, rules_count_map, max_rules,
        probability=1.0 * 2 / 3):
    if len(nodes_map) <= max_bitmaps:
        return

    unassigned_nodes = [n for n in nodes_map]
    num_unassigned_bitmaps = max_bitmaps

    # Assign nodes to bitmaps
    for i in range(max_bitmaps):
        num_nodes_per_bitmap = int(ceil(1.0 * len(unassigned_nodes) / num_unassigned_bitmaps))
        for k in range(min(max_nodes_per_bitmap, num_nodes_per_bitmap), 0, -1):
            min_k_bitmap, min_k_nodes = min_k_union(nodes_map, unassigned_nodes, k, probability)
            redundancy = sum([popcount(min_k_bitmap ^ nodes_map[l]['bitmap']) for l in min_k_nodes])
            if redundancy <= redundancy_per_bitmap:
                for n in min_k_nodes:
                    node = nodes_map[n]
                    node['has_bitmap'] = i
                    node['~bitmap'] = min_k_bitmap ^ node['bitmap']
                break
            else:
                unassigned_nodes += min_k_nodes
        num_unassigned_bitmaps -= 1

    # Add a rule or assign nodes to default bitmap
    default_bitmap = 0
    for n in unassigned_nodes:
        node = nodes_map[n]
        if rules_count_map[n] < max_rules:  # Add a rule in node
            node['has_rule'] = True
            rules_count_map[n] += 1
        else:  # Assign leaf to node bitmap
            default_bitmap |= node['bitmap']

    # Calculate redundancy for nodes assigned to default bitmap
    for n in unassigned_nodes:
        node = nodes_map[n]
        if 'has_rule' not in node:
            node['~bitmap'] = default_bitmap ^ node['bitmap']

    return default_bitmap
