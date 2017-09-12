import sys, os
import numpy as np
from simulation.cloud import *
from simulation.plot import *

TEST_NAME = sys.argv[1]
SEED = int(sys.argv[2])
NUM_BITMAPS = int(sys.argv[3])
LOGS_DIR = sys.argv[4]

print("--- Running test '%s': seed (%s), no. of bitmaps (%s) ---\n" % (TEST_NAME, SEED, NUM_BITMAPS))

np.random.seed(seed=SEED)

if TEST_NAME == 'dcn-cmp':
    NUM_GROUPS = 100000

    cloud = Cloud(num_leafs=576,
                  num_hosts_per_leaf=48,
                  max_vms_per_host=20,
                  num_tenants=3000,
                  min_vms_per_tenant=10,
                  max_vms_per_tenant=5000,
                  vm_dist='expon',
                  num_groups=NUM_GROUPS,
                  min_group_size=5,
                  group_size_dist='uniform',
                  placement_dist='colocate',
                  colocate_num_hosts_per_leaf=48,
                  num_bitmaps=NUM_BITMAPS,
                  generate_bitmaps=True,
                  post_process=True)
elif TEST_NAME == 'baseerat':
    NUM_GROUPS = 100000

    cloud = Cloud(num_leafs=1056,
                  num_hosts_per_leaf=48,
                  max_vms_per_host=20,
                  num_tenants=3000,
                  min_vms_per_tenant=10,
                  max_vms_per_tenant=5000,
                  vm_dist='expon',
                  num_groups=NUM_GROUPS,
                  min_group_size=5,
                  group_size_dist='uniform',
                  placement_dist='colocate',
                  num_bitmaps=NUM_BITMAPS,
                  generate_bitmaps=True,
                  post_process=True)
else:
    raise(Exception('invalid test name'))

data = Data(cloud)

_dir = LOGS_DIR + '/%s/num_bitmaps_%s__seed_%s__num_groups_%s' % (TEST_NAME, NUM_BITMAPS, SEED, NUM_GROUPS)
os.makedirs(_dir, exist_ok=True)

log = Log(data, log_dir=_dir)
