import os
import sys
import random
from simulation.dynamic import Dynamic
from simulation.utils import pickle_dump_obj, pickle_load_obj, marshal_load_obj, marshal_dump_obj

if len(sys.argv) > 1:
    DATA_FILE = sys.argv[9]
    DUMP_FILE_PREFIX = sys.argv[10]

    CLOUD_PARAMS = DATA_FILE.split('.')[-1].split('_')
    SEED = int(CLOUD_PARAMS[-1])
elif True:
    DATA_FILE = 'output/optimizer..'
    DUMP_FILE_PREFIX = 'output/dynamic'

    CLOUD_PARAMS = []
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

dynamic = Dynamic(data)

# pickle_dump_obj(optimizer.data, dump_file)
# marshal_dump_obj(dynamic.data, dump_file)
