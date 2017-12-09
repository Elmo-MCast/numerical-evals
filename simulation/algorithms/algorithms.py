import simulation.algorithms.single_match as single_match
import simulation.algorithms.random_single_match as random_single_match
import simulation.algorithms.exact_match as exact_match
import simulation.algorithms.fuzzy_match as fuzzy_match
import simulation.algorithms.random_fuzzy_match as random_fuzzy_match


def run(algorithm, nodes_map, max_bitmaps, max_nodes_per_bitmap, redundancy_per_bitmap, rules_count_map,
        max_rules, probability):
    if algorithm == 'single-match':
        return single_match.run(nodes_map, max_bitmaps, rules_count_map, max_rules)
    elif algorithm == 'random-single-match':
        return random_single_match.run(nodes_map, max_bitmaps, rules_count_map, max_rules, probability)
    elif algorithm == 'exact-match':
        return exact_match.run(nodes_map, max_bitmaps, max_nodes_per_bitmap, rules_count_map, max_rules)
    elif algorithm == 'fuzzy-match':
        return fuzzy_match.run(nodes_map, max_bitmaps, max_nodes_per_bitmap, redundancy_per_bitmap, rules_count_map,
                               max_rules)
    elif algorithm == 'random-fuzzy-match':
        return random_fuzzy_match.run(nodes_map, max_bitmaps, max_nodes_per_bitmap, redundancy_per_bitmap,
                                      rules_count_map,
                                      max_rules, probability)
    else:
        raise (Exception("invalid algorithm"))
