import sys
import random
from simulation.optimizer import Optimizer
from simulation.utils import pickle_dump_obj, pickle_load_obj

if len(sys.argv) > 1:
    MAX_BATCH_SIZE=int(sys.argv[1])
    ALGORITHM = sys.argv[2]
    NUM_LEAFS_PER_BITMAP = int(sys.argv[3])
    REDUNDANCY_PER_BITMAP = int(sys.argv[4])
    NUM_RULES_PER_LEAF = int(sys.argv[5])
    DATA_FILE = sys.argv[6]
    DUMP_FILE_PREFIX = sys.argv[7]

    CLOUD_PARAMS = DATA_FILE.split('.')[-1].split('_')
    NUM_LEAFS = int(CLOUD_PARAMS[0])
    NUM_BITMAPS = int(CLOUD_PARAMS[13])
    NUM_TENANTS = int(CLOUD_PARAMS[4])
    SEED = int(CLOUD_PARAMS[16])
elif True:
    MAX_BATCH_SIZE = 1
    ALGORITHM = 'single_match'
    NUM_LEAFS_PER_BITMAP = 3
    REDUNDANCY_PER_BITMAP = 2
    NUM_RULES_PER_LEAF = 6400
    DATA_FILE = 'output/cloud.pkl.'
    DUMP_FILE_PREFIX = 'output/optimizer.pkl'

    CLOUD_PARAMS = []
    NUM_LEAFS = 576
    NUM_BITMAPS = 10
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
       DATA_FILE,
       DUMP_FILE_PREFIX,
       NUM_LEAFS,
       NUM_BITMAPS,
       NUM_TENANTS,
       SEED,
       ','.join(CLOUD_PARAMS)))

random.seed(SEED)

data = pickle_load_obj(DATA_FILE)

optimizer = Optimizer(data, max_batch_size=MAX_BATCH_SIZE, algorithm=ALGORITHM,
                      num_leafs_per_bitmap=NUM_LEAFS_PER_BITMAP, redundancy_per_bitmap=REDUNDANCY_PER_BITMAP,
                      num_rules_per_leaf=NUM_RULES_PER_LEAF, num_leafs=NUM_LEAFS, num_bitmaps=NUM_BITMAPS,
                      num_tenants=NUM_TENANTS)

pickle_dump_obj(optimizer.data, DUMP_FILE_PREFIX + "." + "_".join(sys.argv[1:-2]) + "." + "_".join(CLOUD_PARAMS))
