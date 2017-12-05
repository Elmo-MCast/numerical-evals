import os
import sys
import random
from simulation.dynamic import Dynamic
from simulation.data import DynamicData
from simulation.utils import pickle_dump_obj, pickle_load_obj, marshal_load_obj, marshal_dump_obj

if len(sys.argv) > 1:
    NUM_EVENTS = int(sys.argv[1])
    DATA_FILE = sys.argv[2]
    LOG_FILE_PREFIX = sys.argv[3]

    _TEMP = DATA_FILE.split('.')
    CLOUD_PARAMS = _TEMP[-2].split('_')
    NUM_TENANTS = int(CLOUD_PARAMS[3])
    NUM_HOSTS_PER_LEAF = int(CLOUD_PARAMS[1])
    MIN_GROUP_SIZE = int(CLOUD_PARAMS[8])
    SEED = int(CLOUD_PARAMS[14])

    OPTIMIZER_PARAMS = _TEMP[-1].split('_')
    ALGORITHM = OPTIMIZER_PARAMS[1]
    NUM_BITMAPS = int(OPTIMIZER_PARAMS[2])
    NUM_LEAFS_PER_BITMAP = int(OPTIMIZER_PARAMS[3])
    REDUNDANCY_PER_BITMAP = int(OPTIMIZER_PARAMS[4])
    NUM_RULES_PER_LEAF = int(OPTIMIZER_PARAMS[5])
    PROBABILITY_DIVIDEND = int(OPTIMIZER_PARAMS[6])
    PROBABILITY_DIVISOR = int(OPTIMIZER_PARAMS[7])
elif False:
    NUM_EVENTS = 10000
    DATA_FILE = 'output/optimizer..'
    LOG_FILE_PREFIX = 'output/logs'

    CLOUD_PARAMS = []
    NUM_TENANTS = 30
    NUM_HOSTS_PER_LEAF = 48
    MIN_GROUP_SIZE = 5
    SEED = 0

    OPTIMIZER_PARAMS = []
    ALGORITHM = 'exact-match'
    NUM_BITMAPS = 10
    NUM_LEAFS_PER_BITMAP = 3
    REDUNDANCY_PER_BITMAP = 0
    NUM_RULES_PER_LEAF = 100
    PROBABILITY_DIVIDEND = 2
    PROBABILITY_DIVISOR = 3
else:
    raise (Exception('invalid parameters'))

print("""
-> optimizer (
     num_events=%s,
     data_file=%s, 
     dump_file_prefix=%s,
     num_tenants=%s,
     num_hosts_per_leaf=%s,
     min_group_size=%s,
     seed=%s,
     algorithm=%s,
     num_bitmaps=%s,
     num_leafs_per_bitmap=%s,
     redundancy_per_bitmap=%s,
     num_rules_per_leaf=%s,
     probability_dividend=%s,
     probability_divisor=%s,
     cloud_params=[%s],
     optimizer_params=[%s])
""" % (NUM_EVENTS,
       DATA_FILE,
       LOG_FILE_PREFIX,
       NUM_TENANTS,
       NUM_HOSTS_PER_LEAF,
       MIN_GROUP_SIZE,
       SEED,
       ALGORITHM,
       NUM_BITMAPS,
       NUM_LEAFS_PER_BITMAP,
       REDUNDANCY_PER_BITMAP,
       NUM_RULES_PER_LEAF,
       PROBABILITY_DIVIDEND,
       PROBABILITY_DIVISOR,
       ','.join(CLOUD_PARAMS),
       ','.join(OPTIMIZER_PARAMS)))

random.seed(SEED)

log_dir = LOG_FILE_PREFIX + "." + "_".join(CLOUD_PARAMS) + "." + "_".join(OPTIMIZER_PARAMS) \
          + "." + "_".join(sys.argv[1:-2])

if os.path.isdir(log_dir):
    print('%s, already exists.' % log_dir)
    exit(0)

os.system('mkdir -p %s' % log_dir)

# data = pickle_load_obj(DATA_FILE)
data = marshal_load_obj(DATA_FILE)

dynamic = Dynamic(data, num_tenants=NUM_TENANTS, num_events=NUM_EVENTS, algorithm=ALGORITHM, num_bitmaps=NUM_BITMAPS,
                  num_leafs_per_bitmap=NUM_LEAFS_PER_BITMAP, redundancy_per_bitmap=REDUNDANCY_PER_BITMAP,
                  num_rules_per_leaf=NUM_RULES_PER_LEAF, probability=1.0 * PROBABILITY_DIVIDEND / PROBABILITY_DIVISOR,
                  min_group_size=MIN_GROUP_SIZE, num_hosts_per_leaf=NUM_HOSTS_PER_LEAF, debug=False)

data = DynamicData(data, log_dir=log_dir)
data.log()
