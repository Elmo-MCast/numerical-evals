import os
import sys
import random
from simulation.data import Data
from simulation.utils import pickle_load_obj

if len(sys.argv) > 1:
    DATA_FILE = sys.argv[1]
    LOG_DIR = sys.argv[2]

    _TEMP = DATA_FILE.split('.')
    CLOUD_PARAMS = _TEMP[-2].split('_')
    NUM_TENANTS = int(CLOUD_PARAMS[3])
    NUM_LEAFS = int(CLOUD_PARAMS[0])
    NUM_HOSTS_PER_LEAF = int(CLOUD_PARAMS[1])
    SEED = int(CLOUD_PARAMS[-1])

    OPTIMIZER_PARAMS = _TEMP[-1].split('_')
    NUM_BITMAPS = int(OPTIMIZER_PARAMS[2])

elif True:
    DATA_FILE = 'output/optimizer.pkl..'
    LOG_DIR = 'logs/logs'

    CLOUD_PARAMS = []
    NUM_TENANTS = 30
    NUM_LEAFS = 576
    NUM_HOSTS_PER_LEAF = 48
    SEED = 0

    OPTIMIZER_PARAMS = []
    NUM_BITMAPS = 10
else:
    raise (Exception('invalid parameters'))

print("""
-> data (
    num_tenants=%s,
    num_leafs=%s,
    num_hosts_per_leaf=%s,
    num_bitmaps=%s,
    data_file=%s,
    log_dir=%s,
    seed=%s,
    cloud_params=[%s],
    optimizer_params=[%s])
""" %(NUM_TENANTS,
      NUM_LEAFS,
      NUM_HOSTS_PER_LEAF,
      NUM_BITMAPS,
      DATA_FILE,
      LOG_DIR,
      SEED,
      ','.join(CLOUD_PARAMS),
      ','.join(OPTIMIZER_PARAMS)))

random.seed(SEED)

log_dir = LOG_DIR + "/" + "_".join(CLOUD_PARAMS) + "." + "_".join(OPTIMIZER_PARAMS)

if os.path.isdir(log_dir):
    print('%s, already exists.' % log_dir)
    exit(0)

os.system('mkdir -p %s' % log_dir)

data = pickle_load_obj(DATA_FILE)

data = Data(data, num_tenants=NUM_TENANTS, num_leafs=NUM_LEAFS, num_hosts_per_leaf=NUM_HOSTS_PER_LEAF,
            num_bitmaps=NUM_BITMAPS, log_dir=log_dir)

data.log()
