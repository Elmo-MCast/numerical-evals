import sys
import random
from simulation.optimizer import Optimizer
from simulation.utils import load_obj, dump_obj

if len(sys.argv) > 1:
    MAX_BATCH_SIZE=int(sys.argv[1])
    ALGORITHM = sys.argv[2]
    NUM_BITMAPS = int(sys.argv[3])
    NUM_LEAFS_PER_BITMAP = int(sys.argv[4])
    REDUNDANCY_PER_BITMAP = int(sys.argv[5])
    DATA_FILE = sys.argv[6]
    DUMP_FILE = sys.argv[7]
    SEED = int(sys.argv[8])
elif True:
    MAX_BATCH_SIZE = 1
    ALGORITHM = 'single_match'
    NUM_BITMAPS = 5
    NUM_LEAFS_PER_BITMAP = 3
    REDUNDANCY_PER_BITMAP = 2
    DATA_FILE = 'simulation/output/cloud.pkl'
    DUMP_FILE = 'simulation/output/optimizer.pkl'
    SEED = 0
else:
    raise (Exception('invalid parameters'))

print("""
-> optimizer (
     max_batch_size=%s, 
     algorithm=%s, 
     num_bitmaps=%s,
     num_leafs_per_bitmap=%s,
     redundancy_per_bitmap=%s,
     data_file=%s, 
     dump_file=%s,
     seed=%s)
""" % (MAX_BATCH_SIZE,
       ALGORITHM,
       NUM_BITMAPS,
       NUM_LEAFS_PER_BITMAP,
       REDUNDANCY_PER_BITMAP,
       DATA_FILE,
       DUMP_FILE,
       SEED))

random.seed(SEED)

data = load_obj(DATA_FILE)

optimizer = Optimizer(data, max_batch_size=MAX_BATCH_SIZE, algorithm=ALGORITHM, num_bitmaps=NUM_BITMAPS,
                      num_leafs_per_bitmap=NUM_LEAFS_PER_BITMAP, redundancy_per_bitmap=REDUNDANCY_PER_BITMAP)

dump_obj(data, DUMP_FILE)
