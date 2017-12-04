import simulation.algorithms.single_match as single_match
import simulation.algorithms.random_single_match as random_single_match
import simulation.algorithms.exact_match as exact_match
import simulation.algorithms.fuzzy_match as fuzzy_match
import simulation.algorithms.random_fuzzy_match as random_fuzzy_match


def run(algorithm, group, max_bitmaps, max_leafs_per_bitmap, redundancy_per_bitmap, leafs_to_rules_count_map,
        max_rules_per_leaf, probability):
    if algorithm == 'single-match':
        single_match.run(group, max_bitmaps, leafs_to_rules_count_map, max_rules_per_leaf)
    elif algorithm == 'random-single-match':
        random_single_match.run(group, max_bitmaps, leafs_to_rules_count_map, max_rules_per_leaf, probability)
    elif algorithm == 'exact-match':
        exact_match.run(group, max_bitmaps, max_leafs_per_bitmap, leafs_to_rules_count_map, max_rules_per_leaf)
    elif algorithm == 'fuzzy-match':
        fuzzy_match.run(group, max_bitmaps, max_leafs_per_bitmap, redundancy_per_bitmap, leafs_to_rules_count_map,
                        max_rules_per_leaf)
    elif algorithm == 'random-fuzzy-match':
        random_fuzzy_match.run(group, max_bitmaps, max_leafs_per_bitmap, redundancy_per_bitmap, leafs_to_rules_count_map,
                               max_rules_per_leaf, probability)
    else:
        raise (Exception("invalid algorithm"))

