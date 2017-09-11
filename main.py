import sys, os
import numpy as np
from simulation.cloud import *
from simulation.plot import *

SEED = int(sys.argv[1])
NUM_BITMAPS = int(sys.argv[2])
LOGS_DIR = sys.argv[3]

print('--- Running with seed %s, no. of bitmaps: %s ---\n' % (SEED, NUM_BITMAPS))

np.random.seed(seed=SEED)

cloud = Cloud(num_leafs=1056,
              num_hosts_per_leaf=48,
              max_vms_per_host=20,
              num_tenants=3000,
              min_vms_per_tenant=10,
              max_vms_per_tenant=5000,
              vm_dist='expon',
              num_groups=100000,
              min_group_size=5,
              group_size_dist='uniform',
              placement_dist='colocate',
              num_bitmaps=NUM_BITMAPS,
              generate_bitmaps=True,
              post_process=True)

data = Data(cloud)

_dir = LOGS_DIR + '/num_bitmaps_%s__seed_%s' % (NUM_BITMAPS, SEED)
os.makedirs(_dir, exist_ok=True)

log = Log(data, log_dir=_dir)
