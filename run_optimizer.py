import os
import sys
import random
from simulation.optimizer import Optimizer
from simulation.utils import marshal_load_obj, marshal_dump_obj

if len(sys.argv) > 1:
    ALGORITHM = sys.argv[1]
    NUM_BITMAPS = int(sys.argv[2])
    NUM_NODES_PER_BITMAP = int(sys.argv[3])
    REDUNDANCY_PER_BITMAP = int(sys.argv[4])
    NUM_RULES = int(sys.argv[5])
    PROBABILITY_DIVIDEND = int(sys.argv[6])
    PROBABILITY_DIVISOR = int(sys.argv[7])
    NODE_TYPE = sys.argv[8]
    DATA_FILE = sys.argv[9]
    DUMP_FILE_PREFIX = sys.argv[10]

    _TEMP = DATA_FILE.split('.')
    CLOUD_PARAMS = _TEMP[1].split('_')
    NUM_PODS = int(CLOUD_PARAMS[0])
    NUM_LEAFS_PER_POD = int(CLOUD_PARAMS[1])
    NUM_HOSTS_PER_LEAF = int(CLOUD_PARAMS[2])
    NUM_TENANTS = int(CLOUD_PARAMS[4])
    SEED = int(CLOUD_PARAMS[15])

    if len(_TEMP) > 2:
        OPTIMIZER_PARAMS = _TEMP[2].split('_')
    else:
        OPTIMIZER_PARAMS = []
elif False:
    ALGORITHM = 'random-fuzzy-match'
    NUM_BITMAPS = 2
    NUM_NODES_PER_BITMAP = 3
    REDUNDANCY_PER_BITMAP = 6
    NUM_RULES = 100
    PROBABILITY_DIVIDEND = 2
    PROBABILITY_DIVISOR = 3
    NODE_TYPE = 'pods'
    DATA_FILE = 'output/cloud.'
    DUMP_FILE_PREFIX = 'output/optimizer'

    CLOUD_PARAMS = []
    NUM_PODS = 12
    NUM_LEAFS_PER_POD = 48
    NUM_HOSTS_PER_LEAF = 48
    NUM_TENANTS = 3000
    SEED = 0

    OPTIMIZER_PARAMS = []
elif False:
    ALGORITHM = 'random-fuzzy-match'
    NUM_BITMAPS = 10
    NUM_NODES_PER_BITMAP = 3
    REDUNDANCY_PER_BITMAP = 12
    NUM_RULES = 10
    PROBABILITY_DIVIDEND = 2
    PROBABILITY_DIVISOR = 3
    NODE_TYPE = 'leafs'
    DATA_FILE = 'output/optimizer..'
    DUMP_FILE_PREFIX = 'output/optimizer.'

    CLOUD_PARAMS = []
    NUM_PODS = 12
    NUM_LEAFS_PER_POD = 48
    NUM_HOSTS_PER_LEAF = 48
    NUM_TENANTS = 3000
    SEED = 0

    OPTIMIZER_PARAMS = []
elif False:
    ALGORITHM = 'exact-match'
    NUM_BITMAPS = 2
    NUM_NODES_PER_BITMAP = 3
    REDUNDANCY_PER_BITMAP = 0
    NUM_RULES = 100
    PROBABILITY_DIVIDEND = 2
    PROBABILITY_DIVISOR = 3
    NODE_TYPE = 'leafs'
    DATA_FILE = 'output/cloud.'
    DUMP_FILE_PREFIX = 'output/optimizer'

    CLOUD_PARAMS = []
    NUM_PODS = 12
    NUM_LEAFS_PER_POD = 48
    NUM_HOSTS_PER_LEAF = 48
    NUM_TENANTS = 30
    SEED = 0

    OPTIMIZER_PARAMS = []
else:
    raise (Exception('invalid parameters'))

random.seed(SEED)

if OPTIMIZER_PARAMS:
    dump_file = DUMP_FILE_PREFIX + "." + "_".join(CLOUD_PARAMS) + "." + "_".join(OPTIMIZER_PARAMS) + \
                "." + "_".join(sys.argv[1:-2])
else:
    dump_file = DUMP_FILE_PREFIX + "." + "_".join(CLOUD_PARAMS) + "." + "_".join(sys.argv[1:-2])

if os.path.isfile(dump_file):
    print('%s, already exists.' % dump_file)
    exit(0)

data = marshal_load_obj(DATA_FILE)

optimizer = Optimizer(data, algorithm=ALGORITHM, num_bitmaps=NUM_BITMAPS, num_nodes_per_bitmap=NUM_NODES_PER_BITMAP,
                      redundancy_per_bitmap=REDUNDANCY_PER_BITMAP, num_rules=NUM_RULES,
                      num_nodes=(NUM_PODS * NUM_LEAFS_PER_POD) if NODE_TYPE == 'leafs' else NUM_PODS,
                      num_tenants=NUM_TENANTS,
                      probability=1.0 * PROBABILITY_DIVIDEND / PROBABILITY_DIVISOR, node_type=NODE_TYPE,
                      num_ports_per_node=NUM_HOSTS_PER_LEAF if NODE_TYPE == 'leafs' else NUM_LEAFS_PER_POD)

marshal_dump_obj(optimizer.data, dump_file)
