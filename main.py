import sys, os
import numpy as np
from simulation.cloud import *
from simulation.plot import *

TEST_NAME = sys.argv[1]
SEED = int(sys.argv[2])
NUM_BITMAPS = int(sys.argv[3])
NUM_GROUPS = int(sys.argv[4])
NUM_COLOCATE_HOSTS = int(sys.argv[5])
NUM_CAPACITY = int(sys.argv[6])
LOGS_DIR = sys.argv[7]

print("--- Running test '%s': seed (%s), no. of bitmaps (%s), no. of groups (%s), "
      "no. of hosts used for colocated placement (%s), no. of switch rules (%s)  ---\n" %
      (TEST_NAME, SEED, NUM_BITMAPS, NUM_GROUPS, NUM_COLOCATE_HOSTS, NUM_CAPACITY))

np.random.seed(seed=SEED)

if TEST_NAME == 'compare_dcn':
    cloud = Cloud(num_leafs=576,
                  num_hosts_per_leaf=48,
                  num_rules_per_leaf=NUM_CAPACITY,
                  max_vms_per_host=20,
                  num_tenants=3000,
                  min_vms_per_tenant=10,
                  max_vms_per_tenant=5000,
                  vm_dist='expon',  # options: expon, expon-mean, and geom
                  num_groups=NUM_GROUPS,
                  min_group_size=5,
                  group_size_dist='uniform',  # options: uniform and wve
                  placement_dist='colocate',  # options: uniform, colocate, and colocate-random
                  colocate_num_hosts_per_leaf=NUM_COLOCATE_HOSTS,
                  num_bitmaps=NUM_BITMAPS,
                  max_batch_size=1)

elif TEST_NAME == 'baseerat':
    cloud = Cloud(num_leafs=1056,
                  num_hosts_per_leaf=48,
                  num_rules_per_leaf=NUM_CAPACITY,
                  max_vms_per_host=20,
                  num_tenants=3000,
                  min_vms_per_tenant=10,
                  max_vms_per_tenant=5000,
                  vm_dist='expon',  # options: expon, expon-mean, and geom
                  num_groups=NUM_GROUPS,
                  min_group_size=5,
                  group_size_dist='uniform',  # options: uniform and wve
                  placement_dist='colocate',  # options: uniform, colocate, and colocate-random
                  colocate_num_hosts_per_leaf=NUM_COLOCATE_HOSTS,
                  num_bitmaps=NUM_BITMAPS,
                  max_batch_size=1)

else:
    raise(Exception('invalid test name'))

data = Data(cloud)

_dir = LOGS_DIR + '/%s/num_bitmaps_%s__seed_%s__num_groups_%s__num_colocate_hosts_%s__num_capacity_%s' % \
                  (TEST_NAME, NUM_BITMAPS, SEED, NUM_GROUPS, NUM_COLOCATE_HOSTS, NUM_CAPACITY)
os.makedirs(_dir, exist_ok=True)

log = Log(data, log_dir=_dir)
