import sys
import random

from simulation.cloud import Cloud
from simulation.data import Data
from simulation.log import *

if len(sys.argv) > 1:
    NUM_LEAFS = int(sys.argv[1])
    NUM_HOSTS_PER_LEAF = int(sys.argv[2])
    NUM_RULES_PER_LEAF = int(sys.argv[3])
    MAX_VMS_PER_HOST = int(sys.argv[4])
    NUM_TENANTS = int(sys.argv[5])
    MIN_VMS_PER_TENANT = int(sys.argv[6])
    MAX_VMS_PER_TENANT = int(sys.argv[7])
    VM_DIST = sys.argv[8]  # options: expon
    NUM_GROUPS = int(sys.argv[9])
    MIN_GROUP_SIZE = int(sys.argv[10])
    GROUP_SIZE_DIST = sys.argv[11]  # options: uniform and wve
    PLACEMENT_DIST = sys.argv[12]  # options: uniform, colocate-random-linear, and colocate-random-random
    COLOCATE_NUM_HOSTS_PER_LEAF = int(sys.argv[13])
    NUM_BITMAPS = int(sys.argv[14])
    MAX_BATCH_SIZE = int(sys.argv[15])
    SEED = int(sys.argv[16])
    LOGS_DIR = sys.argv[17]
elif False:
    NUM_LEAFS = 576
    NUM_HOSTS_PER_LEAF = 48
    NUM_RULES_PER_LEAF = 1000
    MAX_VMS_PER_HOST = 20
    NUM_TENANTS = 3000
    MIN_VMS_PER_TENANT = 10
    MAX_VMS_PER_TENANT = 5000
    VM_DIST = "expon"  # options: expon
    NUM_GROUPS = 100000
    MIN_GROUP_SIZE = 5
    GROUP_SIZE_DIST = "uniform"  # options: uniform and wve
    PLACEMENT_DIST = "colocate-random-linear"  # options: uniform, colocate-random-linear, and colocate-random-random
    COLOCATE_NUM_HOSTS_PER_LEAF = 48
    NUM_BITMAPS = 10
    MAX_BATCH_SIZE = 1
    SEED = 0
    LOGS_DIR = None
elif True:
    NUM_LEAFS = 576
    NUM_HOSTS_PER_LEAF = 48
    NUM_RULES_PER_LEAF = 10000
    MAX_VMS_PER_HOST = 20
    NUM_TENANTS = 3000
    MIN_VMS_PER_TENANT = 10
    MAX_VMS_PER_TENANT = 5000
    VM_DIST = "expon"  # options: expon
    NUM_GROUPS = 1000
    MIN_GROUP_SIZE = 5
    GROUP_SIZE_DIST = "uniform"  # options: uniform and wve
    PLACEMENT_DIST = "colocate-random-linear"  # options: uniform, colocate-random-linear, and colocate-random-random
    COLOCATE_NUM_HOSTS_PER_LEAF = 48
    NUM_BITMAPS = 10
    MAX_BATCH_SIZE = 1
    SEED = 0
    LOGS_DIR = None
else:
    raise (Exception('invalid parameters'))

print("""
-> cloud (
     leafs=%s, 
     hosts_per_leaf=%s, 
     rules_per_leaf=%s,
     vms_per_host=%s,
     tenants=%s, 
     min_vms_per_tenant=%s,
     max_vms_per_tenant=%s,
     vm_dist=%s,
     groups=%s,
     min_group_size=%s,
     group_size_dist=%s,
     placement_dist=%s,
     colocate_hosts_per_leaf=%s,
     bitmaps=%s,
     batch_size=%s,
     seed=%s)
""" % (NUM_LEAFS,
       NUM_HOSTS_PER_LEAF,
       NUM_RULES_PER_LEAF,
       MAX_VMS_PER_HOST,
       NUM_TENANTS,
       MIN_VMS_PER_TENANT,
       MAX_VMS_PER_TENANT,
       VM_DIST,
       NUM_GROUPS,
       MIN_GROUP_SIZE,
       GROUP_SIZE_DIST,
       PLACEMENT_DIST,
       COLOCATE_NUM_HOSTS_PER_LEAF,
       NUM_BITMAPS,
       MAX_BATCH_SIZE,
       SEED))

random.seed(SEED)

cloud = Cloud(num_leafs=NUM_LEAFS,
              num_hosts_per_leaf=NUM_HOSTS_PER_LEAF,
              num_rules_per_leaf=NUM_RULES_PER_LEAF,
              max_vms_per_host=MAX_VMS_PER_HOST,
              num_tenants=NUM_TENANTS,
              min_vms_per_tenant=MIN_VMS_PER_TENANT,
              max_vms_per_tenant=MAX_VMS_PER_TENANT,
              vm_dist=VM_DIST,  # options: expon, expon-mean, and geom
              num_groups=NUM_GROUPS,
              min_group_size=MIN_GROUP_SIZE,
              group_size_dist=GROUP_SIZE_DIST,  # options: uniform and wve
              placement_dist=PLACEMENT_DIST,  # options: uniform, colocate-random-linear, and colocate-random-random
              colocate_num_hosts_per_leaf=COLOCATE_NUM_HOSTS_PER_LEAF,
              num_bitmaps=NUM_BITMAPS,
              max_batch_size=MAX_BATCH_SIZE)

# data = Data(cloud)

# if LOGS_DIR:
#     _dir = LOGS_DIR + '/mcast-dcn/seed/%s/bitmaps/%s/colocate-hosts/%s' % \
#                       (SEED, NUM_BITMAPS, COLOCATE_NUM_HOSTS_PER_LEAF)
#     os.makedirs(_dir, exist_ok=True)
#
#     log = Log(data, log_dir=_dir)
