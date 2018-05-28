import os
import sys
import random
from simulation.dynamic import Dynamic
from simulation.utils import marshal_load_obj, marshal_dump_obj

if len(sys.argv) > 1:
    NUM_EVENTS = int(sys.argv[1])
    FAILED_NODE_TYPE = sys.argv[2]
    NUM_SPINES_PER_POD = int(sys.argv[3])
    DATA_FILE = sys.argv[4]
    DUMP_FILE_PREFIX = sys.argv[5]

    _TEMP = DATA_FILE.split('.')
    CLOUD_PARAMS = _TEMP[1].split('_')
    NUM_PODS = int(CLOUD_PARAMS[0])
    NUM_LEAFS_PER_POD = int(CLOUD_PARAMS[1])
    NUM_HOSTS_PER_LEAF = int(CLOUD_PARAMS[2])
    NUM_TENANTS = int(CLOUD_PARAMS[4])
    MIN_GROUP_SIZE = int(CLOUD_PARAMS[9])
    SEED = int(CLOUD_PARAMS[15])

    PODS_OPTIMIZER_PARAMS = _TEMP[2].split('_')
    PODS_ALGORITHM = PODS_OPTIMIZER_PARAMS[0]
    PODS_NUM_BITMAPS = int(PODS_OPTIMIZER_PARAMS[1])
    PODS_NUM_NODES_PER_BITMAP = int(PODS_OPTIMIZER_PARAMS[2])
    PODS_REDUNDANCY_PER_BITMAP = int(PODS_OPTIMIZER_PARAMS[3])
    PODS_NUM_RULES = int(PODS_OPTIMIZER_PARAMS[4])
    PODS_PROBABILITY_DIVIDEND = int(PODS_OPTIMIZER_PARAMS[5])
    PODS_PROBABILITY_DIVISOR = int(PODS_OPTIMIZER_PARAMS[6])

    LEAFS_OPTIMIZER_PARAMS = _TEMP[3].split('_')
    LEAFS_ALGORITHM = LEAFS_OPTIMIZER_PARAMS[0]
    LEAFS_NUM_BITMAPS = int(LEAFS_OPTIMIZER_PARAMS[1])
    LEAFS_NUM_NODES_PER_BITMAP = int(LEAFS_OPTIMIZER_PARAMS[2])
    LEAFS_REDUNDANCY_PER_BITMAP = int(LEAFS_OPTIMIZER_PARAMS[3])
    LEAFS_NUM_RULES = int(LEAFS_OPTIMIZER_PARAMS[4])
    LEAFS_PROBABILITY_DIVIDEND = int(LEAFS_OPTIMIZER_PARAMS[5])
    LEAFS_PROBABILITY_DIVISOR = int(LEAFS_OPTIMIZER_PARAMS[6])

    DEBUG = True
elif True:
    NUM_EVENTS = 10000
    FAILED_NODE_TYPE = 'core'
    NUM_SPINES_PER_POD = 4
    DATA_FILE = 'output/optimizer.12_48_48_20_30_10_5000_expon_1000_5_uniform_colocate-uniform_48_True_5_0.random-fuzzy-match_1_1_0_5_2_3_pods.random-fuzzy-match_5_2_6_100_2_3_leafs'
    # DATA_FILE = 'output/optimizer.12_48_48_20_3000_10_5000_expon_100000_5_uniform_colocate-uniform_48_True_5_0.random-fuzzy-match_2_3_6_1000_2_3_pods.random-fuzzy-match_10_3_12_10000_2_3_leafs'
    DUMP_FILE_PREFIX = 'output/dynamic_with_failures'

    _TEMP = DATA_FILE.split('.')
    CLOUD_PARAMS = _TEMP[1].split('_')
    NUM_PODS = int(CLOUD_PARAMS[0])
    NUM_LEAFS_PER_POD = int(CLOUD_PARAMS[1])
    NUM_HOSTS_PER_LEAF = int(CLOUD_PARAMS[2])
    NUM_TENANTS = int(CLOUD_PARAMS[4])
    MIN_GROUP_SIZE = int(CLOUD_PARAMS[9])
    SEED = int(CLOUD_PARAMS[15])

    PODS_OPTIMIZER_PARAMS = _TEMP[2].split('_')
    PODS_ALGORITHM = PODS_OPTIMIZER_PARAMS[0]
    PODS_NUM_BITMAPS = int(PODS_OPTIMIZER_PARAMS[1])
    PODS_NUM_NODES_PER_BITMAP = int(PODS_OPTIMIZER_PARAMS[2])
    PODS_REDUNDANCY_PER_BITMAP = int(PODS_OPTIMIZER_PARAMS[3])
    PODS_NUM_RULES = int(PODS_OPTIMIZER_PARAMS[4])
    PODS_PROBABILITY_DIVIDEND = int(PODS_OPTIMIZER_PARAMS[5])
    PODS_PROBABILITY_DIVISOR = int(PODS_OPTIMIZER_PARAMS[6])

    LEAFS_OPTIMIZER_PARAMS = _TEMP[3].split('_')
    LEAFS_ALGORITHM = LEAFS_OPTIMIZER_PARAMS[0]
    LEAFS_NUM_BITMAPS = int(LEAFS_OPTIMIZER_PARAMS[1])
    LEAFS_NUM_NODES_PER_BITMAP = int(LEAFS_OPTIMIZER_PARAMS[2])
    LEAFS_REDUNDANCY_PER_BITMAP = int(LEAFS_OPTIMIZER_PARAMS[3])
    LEAFS_NUM_RULES = int(LEAFS_OPTIMIZER_PARAMS[4])
    LEAFS_PROBABILITY_DIVIDEND = int(LEAFS_OPTIMIZER_PARAMS[5])
    LEAFS_PROBABILITY_DIVISOR = int(LEAFS_OPTIMIZER_PARAMS[6])

    DEBUG = True
elif False:
    NUM_EVENTS = 10000
    FAILED_NODE_TYPE = 'spine'
    NUM_SPINES_PER_POD = 4
    DATA_FILE = 'output/optimizer..'
    DUMP_FILE_PREFIX = 'output/dynamic_with_failures'

    CLOUD_PARAMS = []
    NUM_PODS = 12
    NUM_LEAFS_PER_POD = 48
    NUM_HOSTS_PER_LEAF = 48
    NUM_TENANTS = 30
    MIN_GROUP_SIZE = 5
    SEED = 0

    PODS_OPTIMIZER_PARAMS = []
    PODS_ALGORITHM = 'exact-match'
    PODS_NUM_BITMAPS = 2
    PODS_NUM_NODES_PER_BITMAP = 3
    PODS_REDUNDANCY_PER_BITMAP = 0
    PODS_NUM_RULES = 100
    PODS_PROBABILITY_DIVIDEND = 2
    PODS_PROBABILITY_DIVISOR = 3

    LEAFS_OPTIMIZER_PARAMS = []
    LEAFS_ALGORITHM = 'exact-match'
    LEAFS_NUM_BITMAPS = 10
    LEAFS_NUM_NODES_PER_BITMAP = 3
    LEAFS_REDUNDANCY_PER_BITMAP = 0
    LEAFS_NUM_RULES = 100
    LEAFS_PROBABILITY_DIVIDEND = 2
    LEAFS_PROBABILITY_DIVISOR = 3

    DEBUG = True
else:
    raise (Exception('invalid parameters'))

random.seed(SEED)

dump_file = DUMP_FILE_PREFIX + "." + "_".join(CLOUD_PARAMS) + "." + "_".join(PODS_OPTIMIZER_PARAMS) \
            + "." + "_".join(LEAFS_OPTIMIZER_PARAMS) + "." + "_".join(sys.argv[1:-2])

if os.path.isfile(dump_file):
    print('%s, already exists.' % dump_file)
    exit(0)

data = marshal_load_obj(DATA_FILE)

dynamic = Dynamic(data, num_events=NUM_EVENTS, num_pods=NUM_PODS, num_leafs_per_pod=NUM_LEAFS_PER_POD,
                  num_hosts_per_leaf=NUM_HOSTS_PER_LEAF, num_tenants=NUM_TENANTS, min_group_size=MIN_GROUP_SIZE,
                  pods_algorithm=PODS_ALGORITHM, pods_num_bitmaps=PODS_NUM_BITMAPS,
                  pods_num_nodes_per_bitmap=PODS_NUM_NODES_PER_BITMAP,
                  pods_redundancy_per_bitmap=PODS_REDUNDANCY_PER_BITMAP, pods_num_rules=PODS_NUM_RULES,
                  pods_probability=1.0 * PODS_PROBABILITY_DIVIDEND / PODS_PROBABILITY_DIVISOR,
                  leafs_algorithm=LEAFS_ALGORITHM, leafs_num_bitmaps=LEAFS_NUM_BITMAPS,
                  leafs_num_nodes_per_bitmap=LEAFS_NUM_NODES_PER_BITMAP,
                  leafs_redundancy_per_bitmap=LEAFS_REDUNDANCY_PER_BITMAP, leafs_num_rules=LEAFS_NUM_RULES,
                  leafs_probability=1.0 * LEAFS_PROBABILITY_DIVIDEND / LEAFS_PROBABILITY_DIVISOR,
                  with_failures=True, failed_node_type=FAILED_NODE_TYPE, num_spines_per_pod=NUM_SPINES_PER_POD,
                  debug=DEBUG)

marshal_dump_obj(dynamic.data, dump_file)
