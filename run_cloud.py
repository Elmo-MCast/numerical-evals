import os
import sys
import random
from simulation.cloud import Cloud
from simulation.utils import bar_range, pickle_dump_obj, marshal_dump_obj

if len(sys.argv) > 1:
    NUM_PODS = int(sys.argv[1])
    NUM_LEAFS_PER_POD = int(sys.argv[2])
    NUM_HOSTS_PER_LEAF = int(sys.argv[3])
    MAX_VMS_PER_HOST = int(sys.argv[4])
    NUM_TENANTS = int(sys.argv[5])
    MIN_VMS_PER_TENANT = int(sys.argv[6])
    MAX_VMS_PER_TENANT = int(sys.argv[7])
    VM_DIST = sys.argv[8]  # options: expon
    NUM_GROUPS = int(sys.argv[9])
    MIN_GROUP_SIZE = int(sys.argv[10])
    GROUP_SIZE_DIST = sys.argv[11]  # options: uniform and wve
    MULTI_THREADED = True if sys.argv[12] == 'True' else False
    NUM_JOBS = int(sys.argv[13])
    SEED = int(sys.argv[14])
    DUMP_FILE_PREFIX = sys.argv[15]
elif False:
    NUM_PODS = 12
    NUM_LEAFS_PER_POD = 48
    NUM_HOSTS_PER_LEAF = 48
    MAX_VMS_PER_HOST = 20
    NUM_TENANTS = 3000
    MIN_VMS_PER_TENANT = 10
    MAX_VMS_PER_TENANT = 5000
    VM_DIST = "expon"  # options: expon
    NUM_GROUPS = 100000
    MIN_GROUP_SIZE = 5
    GROUP_SIZE_DIST = "uniform"  # options: uniform and wve
    MULTI_THREADED = True
    NUM_JOBS = 5
    SEED = 0
    DUMP_FILE_PREFIX = 'output/cloud'
elif False:
    NUM_PODS = 12
    NUM_LEAFS_PER_POD = 48
    NUM_HOSTS_PER_LEAF = 48
    MAX_VMS_PER_HOST = 20
    NUM_TENANTS = 30
    MIN_VMS_PER_TENANT = 10
    MAX_VMS_PER_TENANT = 5000
    VM_DIST = "expon"  # options: expon
    NUM_GROUPS = 1000
    MIN_GROUP_SIZE = 5
    GROUP_SIZE_DIST = "wve"  # options: uniform and wve
    MULTI_THREADED = True
    NUM_JOBS = 5
    SEED = 0
    DUMP_FILE_PREFIX = 'output/cloud'
else:
    raise (Exception('invalid parameters'))

random.seed(SEED)

dump_file = DUMP_FILE_PREFIX + "." + "_".join(sys.argv[1:-1])

if os.path.isfile(dump_file):
    print('%s, already exists.' % dump_file)
    exit(0)

cloud = Cloud(num_pods=NUM_PODS,
              num_leafs_per_pod=NUM_LEAFS_PER_POD,
              num_hosts_per_leaf=NUM_HOSTS_PER_LEAF,
              max_vms_per_host=MAX_VMS_PER_HOST,
              num_tenants=NUM_TENANTS,
              min_vms_per_tenant=MIN_VMS_PER_TENANT,
              max_vms_per_tenant=MAX_VMS_PER_TENANT,
              vm_dist=VM_DIST,
              num_groups=NUM_GROUPS,
              min_group_size=MIN_GROUP_SIZE,
              group_size_dist=GROUP_SIZE_DIST,
              multi_threaded=MULTI_THREADED,
              num_jobs=NUM_JOBS)

# pickle_dump_obj(cloud.data, dump_file)
marshal_dump_obj(cloud.data, dump_file)
