import sys
import random
from simulation.data import Data
from simulation.utils import pickle_load_obj, pickle_dump_obj

if len(sys.argv) > 1:
    DATA_FILE = sys.argv[1]
    LOG_DIR = sys.argv[2]

    CLOUD_PARAMS = DATA_FILE.split('.')[-1].split('_')
    NUM_TENANTS = int(CLOUD_PARAMS[4])
    NUM_HOSTS_PER_LEAF = int(CLOUD_PARAMS[4])
    NUM_BITMAPS = int(CLOUD_PARAMS[13])
    SEED = int(CLOUD_PARAMS[16])
elif True:
    DATA_FILE = 'output/optimizer.pkl..'
    LOG_DIR = 'output/log'

    CLOUD_PARAMS = []
    NUM_TENANTS = 30
    NUM_HOSTS_PER_LEAF = 48
    NUM_BITMAPS = 10
    SEED = 0
else:
    raise (Exception('invalid parameters'))

print("""
-> data (
    num_tenants=%s,
    num_hosts_per_leaf=%s,
    num_bitmaps=%s,
    data_file=%s,
    log_dir=%s,
    seed=%s)
""" %(NUM_TENANTS,
      NUM_HOSTS_PER_LEAF,
      NUM_BITMAPS,
      DATA_FILE,
      LOG_DIR,
      SEED))

random.seed(SEED)

data = pickle_load_obj(DATA_FILE)

data = Data(data, num_tenants=NUM_TENANTS, num_hosts_per_leaf=NUM_HOSTS_PER_LEAF, num_bitmaps=NUM_BITMAPS,
            log_dir=LOG_DIR)

data.log()
