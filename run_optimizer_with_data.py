import os
import sys
import random
from simulation.optimizer import Optimizer
from simulation.data import Data
from simulation.utils import marshal_load_obj

if len(sys.argv) > 1:
    ALGORITHM = sys.argv[1]
    NUM_BITMAPS = int(sys.argv[2])
    NUM_NODES_PER_BITMAP = int(sys.argv[3])
    REDUNDANCY_PER_BITMAP = int(sys.argv[4])
    NUM_RULES = int(sys.argv[5])
    PROBABILITY_DIVIDEND = int(sys.argv[6])
    PROBABILITY_DIVISOR = int(sys.argv[7])
    NODE_TYPE = sys.argv[8]
    LOG_CLOUD_STATS = True if sys.argv[9] == 'True' else False
    DATA_FILE = sys.argv[10]
    LOG_FILE_PREFIX = sys.argv[11]

    _TEMP = DATA_FILE.split('.')
    CLOUD_PARAMS = _TEMP[1].split('_')
    NUM_PODS = int(CLOUD_PARAMS[0])
    NUM_LEAFS_PER_POD = int(CLOUD_PARAMS[1])
    NUM_HOSTS_PER_LEAF = int(CLOUD_PARAMS[2])
    NUM_TENANTS = int(CLOUD_PARAMS[4])
    SEED = int(CLOUD_PARAMS[15])

    if len(_TEMP) > 2:
        OPTIMIZER_PARAMS = _TEMP[2].split('_')
        NODE_TYPE_0 = OPTIMIZER_PARAMS[7]
    else:
        OPTIMIZER_PARAMS = []
        NODE_TYPE_0 = None
elif False:
    ALGORITHM = 'random-fuzzy-match'
    NUM_BITMAPS = 2
    NUM_NODES_PER_BITMAP = 2
    REDUNDANCY_PER_BITMAP = 0
    NUM_RULES = 100
    PROBABILITY_DIVIDEND = 2
    PROBABILITY_DIVISOR = 3
    NODE_TYPE = 'pods'
    LOG_CLOUD_STATS = True
    DATA_FILE = 'output/cloud.'
    LOG_FILE_PREFIX = 'output/logs'

    CLOUD_PARAMS = []
    NUM_PODS = 12
    NUM_LEAFS_PER_POD = 48
    NUM_HOSTS_PER_LEAF = 48
    NUM_TENANTS = 3000
    SEED = 0

    OPTIMIZER_PARAMS = []
    NODE_TYPE_0 = None
elif False:
    ALGORITHM = 'random-fuzzy-match'
    NUM_BITMAPS = 20
    NUM_NODES_PER_BITMAP = 3
    REDUNDANCY_PER_BITMAP = 0
    NUM_RULES = 5000
    PROBABILITY_DIVIDEND = 2
    PROBABILITY_DIVISOR = 3
    NODE_TYPE = 'leafs'
    LOG_CLOUD_STATS = True
    DATA_FILE = 'output/optimizer..'
    LOG_FILE_PREFIX = 'output/logs'

    CLOUD_PARAMS = []
    NUM_PODS = 12
    NUM_LEAFS_PER_POD = 48
    NUM_HOSTS_PER_LEAF = 48
    NUM_TENANTS = 3000
    SEED = 0

    OPTIMIZER_PARAMS = []
    NODE_TYPE_0 = None
elif False:
    ALGORITHM = 'exact-match'
    NUM_BITMAPS = 2
    NUM_NODES_PER_BITMAP = 3
    REDUNDANCY_PER_BITMAP = 0
    NUM_RULES = 100
    PROBABILITY_DIVIDEND = 2
    PROBABILITY_DIVISOR = 3
    NODE_TYPE = 'leafs'
    LOG_CLOUD_STATS = True
    DATA_FILE = 'output/cloud.'
    LOG_FILE_PREFIX = 'output/logs'

    CLOUD_PARAMS = []
    NUM_PODS = 12
    NUM_LEAFS_PER_POD = 48
    NUM_HOSTS_PER_LEAF = 48
    NUM_TENANTS = 30
    SEED = 0

    OPTIMIZER_PARAMS = []
    NODE_TYPE_0 = None
else:
    raise (Exception('invalid parameters'))

random.seed(SEED)

if OPTIMIZER_PARAMS:
    log_dir = LOG_FILE_PREFIX + "." + "_".join(CLOUD_PARAMS) + "." + "_".join(OPTIMIZER_PARAMS) + \
                "." + "_".join(sys.argv[1:-2])
else:
    log_dir = LOG_FILE_PREFIX + "." + "_".join(CLOUD_PARAMS) + "." + "_".join(sys.argv[1:-2])

if os.path.isdir(log_dir):
    print('%s, already exists.' % log_dir)
    exit(0)

os.system('mkdir -p %s' % log_dir)

data = marshal_load_obj(DATA_FILE)

optimizer = Optimizer(data, algorithm=ALGORITHM, num_bitmaps=NUM_BITMAPS, num_nodes_per_bitmap=NUM_NODES_PER_BITMAP,
                      redundancy_per_bitmap=REDUNDANCY_PER_BITMAP, num_rules=NUM_RULES,
                      num_nodes=(NUM_PODS * NUM_LEAFS_PER_POD) if NODE_TYPE == 'leafs' else NUM_PODS,
                      num_tenants=NUM_TENANTS,
                      probability=1.0 * PROBABILITY_DIVIDEND / PROBABILITY_DIVISOR, node_type=NODE_TYPE)

if NODE_TYPE_0:
    data = Data(data, num_tenants=NUM_TENANTS, num_pods=NUM_PODS, num_leafs_per_pod=NUM_LEAFS_PER_POD,
                num_hosts_per_leaf=NUM_HOSTS_PER_LEAF, log_dir=log_dir, node_type_0=NODE_TYPE_0, node_type_1=NODE_TYPE)
else:
    data = Data(data, num_tenants=NUM_TENANTS, num_pods=NUM_PODS, num_leafs_per_pod=NUM_LEAFS_PER_POD,
                num_hosts_per_leaf=NUM_HOSTS_PER_LEAF, log_dir=log_dir, node_type_0=NODE_TYPE, node_type_1=None)

data.log_stats(log_cloud_stats=LOG_CLOUD_STATS)
