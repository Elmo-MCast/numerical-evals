import os
import sys
import random
from simulation.optimizer import Optimizer
from simulation.data import Data
from simulation.utils import pickle_dump_obj, pickle_load_obj, marshal_load_obj

if len(sys.argv) > 1:
    MAX_BATCH_SIZE = int(sys.argv[1])
    ALGORITHM = sys.argv[2]
    NUM_BITMAPS = int(sys.argv[3])
    NUM_LEAFS_PER_BITMAP = int(sys.argv[4])
    REDUNDANCY_PER_BITMAP = int(sys.argv[5])
    NUM_RULES_PER_LEAF = int(sys.argv[6])
    PROBABILITY_DIVIDEND = int(sys.argv[7])
    PROBABILITY_DIVISOR = int(sys.argv[8])
    DATA_FILE = sys.argv[9]
    LOG_FILE_PREFIX = sys.argv[10]

    CLOUD_PARAMS = DATA_FILE.split('.')[-1].split('_')
    NUM_LEAFS = int(CLOUD_PARAMS[0])
    NUM_HOSTS_PER_LEAF = int(CLOUD_PARAMS[1])
    NUM_TENANTS = int(CLOUD_PARAMS[3])
    SEED = int(CLOUD_PARAMS[14])
elif False:
    MAX_BATCH_SIZE = 1
    ALGORITHM = 'fuzzy-match'
    NUM_BITMAPS = 14
    NUM_LEAFS_PER_BITMAP = 3
    REDUNDANCY_PER_BITMAP = 0
    NUM_RULES_PER_LEAF = 100
    PROBABILITY_DIVIDEND = 2
    PROBABILITY_DIVISOR = 3
    DATA_FILE = 'output/cloud.'
    LOG_FILE_PREFIX = 'output/logs'

    CLOUD_PARAMS = []
    NUM_LEAFS = 576
    NUM_HOSTS_PER_LEAF = 48
    NUM_TENANTS = 30
    SEED = 0
else:
    raise (Exception('invalid parameters'))

print("""
-> optimizer (
     max_batch_size=%s, 
     algorithm=%s, 
     num_leafs_per_bitmap=%s,
     redundancy_per_bitmap=%s,
     num_rules_per_leaf=%s,
     probability_dividend=%s,
     probability_divisor=%s,
     data_file=%s, 
     dump_file_prefix=%s,
     num_leafs=%s,
     num_bitmaps=%s,
     num_tenants=%s,
     seed=%s,
     cloud_params=[%s])
""" % (MAX_BATCH_SIZE,
       ALGORITHM,
       NUM_LEAFS_PER_BITMAP,
       REDUNDANCY_PER_BITMAP,
       NUM_RULES_PER_LEAF,
       PROBABILITY_DIVIDEND,
       PROBABILITY_DIVISOR,
       DATA_FILE,
       LOG_FILE_PREFIX,
       NUM_LEAFS,
       NUM_BITMAPS,
       NUM_TENANTS,
       SEED,
       ','.join(CLOUD_PARAMS)))

random.seed(SEED)

log_dir = LOG_FILE_PREFIX + "." + "_".join(CLOUD_PARAMS) + "." + "_".join(sys.argv[1:-2])

if os.path.isdir(log_dir):
    print('%s, already exists.' % log_dir)
    exit(0)

os.system('mkdir -p %s' % log_dir)

# data = pickle_load_obj(DATA_FILE)
data = marshal_load_obj(DATA_FILE)

optimizer = Optimizer(data, max_batch_size=MAX_BATCH_SIZE, algorithm=ALGORITHM,
                      num_leafs_per_bitmap=NUM_LEAFS_PER_BITMAP, redundancy_per_bitmap=REDUNDANCY_PER_BITMAP,
                      num_rules_per_leaf=NUM_RULES_PER_LEAF, num_leafs=NUM_LEAFS, num_bitmaps=NUM_BITMAPS,
                      num_tenants=NUM_TENANTS, probability=1.0 * PROBABILITY_DIVIDEND / PROBABILITY_DIVISOR)

data = Data(data, num_tenants=NUM_TENANTS, num_leafs=NUM_LEAFS, num_hosts_per_leaf=NUM_HOSTS_PER_LEAF,
            num_bitmaps=NUM_BITMAPS, log_dir=log_dir)
data.log()
