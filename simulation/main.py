import sys, os
import numpy as np

sys.path.append("../")
from simulation.cloud import *
from simulation.data import *
from simulation.plot import *
from simulation.log import *

TEST_NAME = "mcast-dcn"
SEED = 1
NUM_BITMAPS = 10
NUM_GROUPS = 100000
NUM_COLOCATE_HOSTS = 48
NUM_CAPACITY = 1000

print("--- Running test '%s': seed (%s), bitmaps (%s), groups (%s), "
      "hosts used for colocated placement (%s), switch rules (%s)  ---\n" %
      (TEST_NAME, SEED, NUM_BITMAPS, NUM_GROUPS, NUM_COLOCATE_HOSTS, NUM_CAPACITY))

np.random.seed(seed=SEED)

if TEST_NAME == 'mcast-dcn':
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
                  placement_dist='colocate-linear',  # options: uniform, colocate-linear, and colocate-random
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
