import os
import sys
import random
from simulation.dynamic import Dynamic
from simulation.utils import pickle_dump_obj, pickle_load_obj, marshal_load_obj, marshal_dump_obj

if len(sys.argv) > 1:
    DATA_FILE = sys.argv[9]
    DUMP_FILE_PREFIX = sys.argv[10]

    CLOUD_PARAMS = DATA_FILE.split('.')[-1].split('_')
    NUM_TENANTS = int(CLOUD_PARAMS[3])
    SEED = int(CLOUD_PARAMS[-1])
elif True:
    NUM_EVENTS = 10000
    DATA_FILE = 'output/optimizer..'
    DUMP_FILE_PREFIX = 'output/dynamic'

    CLOUD_PARAMS = []
    NUM_TENANTS = 30
    ALGORITHM = 'exact-match'
    NUM_BITMAPS = 10
    NUM_LEAFS_PER_BITMAP = 3
    REDUNDANCY_PER_BITMAP = 0
    NUM_RULES_PER_LEAF = 100
    PROBABILITY_DIVIDEND = 2
    PROBABILITY_DIVISOR = 3
    MIN_GROUP_SIZE = 5
    NUM_HOSTS_PER_LEAF = 48
    SEED = 0
else:
    raise (Exception('invalid parameters'))

print("""
-> optimizer (
     data_file=%s, 
     dump_file_prefix=%s,
     seed=%s,
     cloud_params=[%s])
""" % (DATA_FILE,
       DUMP_FILE_PREFIX,
       SEED,
       ','.join(CLOUD_PARAMS)))

random.seed(SEED)

dump_file = DUMP_FILE_PREFIX + "." + "_".join(CLOUD_PARAMS) + "." + "_".join(sys.argv[1:-2])

if os.path.isfile(dump_file):
    print('%s, already exists.' % dump_file)
    exit(0)

# data = pickle_load_obj(DATA_FILE)
data = marshal_load_obj(DATA_FILE)

dynamic = Dynamic(data, num_tenants=NUM_TENANTS, num_events=NUM_EVENTS, algorithm=ALGORITHM, num_bitmaps=NUM_BITMAPS,
                  num_leafs_per_bitmap=NUM_LEAFS_PER_BITMAP, redundancy_per_bitmap=REDUNDANCY_PER_BITMAP,
                  num_rules_per_leaf=NUM_RULES_PER_LEAF, probability=1.0 * PROBABILITY_DIVIDEND / PROBABILITY_DIVISOR,
                  min_group_size=MIN_GROUP_SIZE, num_hosts_per_leaf=NUM_HOSTS_PER_LEAF, debug=False)

# pickle_dump_obj(optimizer.data, dump_file)
# marshal_dump_obj(dynamic.data, dump_file)
