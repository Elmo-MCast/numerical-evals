from fabric.api import *

NUM_PODS = 12
NUM_LEAFS_PER_POD = 48
NUM_HOSTS_PER_LEAF = 48
MAX_VMS_PER_HOST = 20
NUM_TENANTS = 3000
MIN_VMS_PER_TENANT = 10
MAX_VMS_PER_TENANT = 5000
VM_DIST = 'expon'  # options: expon
NUM_GROUPS = 1000000
MIN_GROUP_SIZE = 5
GROUP_SIZE_DIST = 'uniform'  # options: uniform and wve
PLACEMENT_DIST = "colocate-uniform"  # options: colocate-uniform, colocate-colocate-uniform
PLACEMENT_NUM_HOSTS_PER_LEAF = 48
MULTI_THREADED = True
NUM_JOBS = 5
SEED = 0
DUMP_FILE_PREFIX = "/mnt/sdb1/baseerat/numerical-evals/12-11-2017/output-1M/cloud"

PYTHON = "pypy3"  # options: pypy3 or python or python3


def run_cloud(params):
    local('%s run_cloud.py %s' % (PYTHON, ' '.join(map(str, params))))


def kill():
    local('pkill -f run_cloud')


def test_small():
    DUMP_FILE_PREFIX = 'output/cloud'
    NUM_TENANTS = 30
    NUM_GROUPS = 1000
    PLACEMENT_DIST = "colocate-uniform"

    run_cloud([NUM_PODS,
               NUM_LEAFS_PER_POD,
               NUM_HOSTS_PER_LEAF,
               MAX_VMS_PER_HOST,
               NUM_TENANTS,
               MIN_VMS_PER_TENANT,
               MAX_VMS_PER_TENANT,
               VM_DIST,
               NUM_GROUPS,
               MIN_GROUP_SIZE,
               GROUP_SIZE_DIST,
               PLACEMENT_DIST,
               PLACEMENT_NUM_HOSTS_PER_LEAF,
               MULTI_THREADED,
               NUM_JOBS,
               SEED,
               DUMP_FILE_PREFIX])


def test_large():
    DUMP_FILE_PREFIX = 'output/cloud'
    NUM_TENANTS = 3000
    NUM_GROUPS = 100000
    PLACEMENT_DIST = "colocate-uniform"

    run_cloud([NUM_PODS,
               NUM_LEAFS_PER_POD,
               NUM_HOSTS_PER_LEAF,
               MAX_VMS_PER_HOST,
               NUM_TENANTS,
               MIN_VMS_PER_TENANT,
               MAX_VMS_PER_TENANT,
               VM_DIST,
               NUM_GROUPS,
               MIN_GROUP_SIZE,
               GROUP_SIZE_DIST,
               PLACEMENT_DIST,
               PLACEMENT_NUM_HOSTS_PER_LEAF,
               MULTI_THREADED,
               NUM_JOBS,
               SEED,
               DUMP_FILE_PREFIX])


def run():
    for seed in [0, 1, 2]:
        for group_size_dist in ['uniform', 'wve']:
            for placement_dist in ['colocate-colocate-uniform', 'colocate-uniform']:
                if placement_dist == 'colocate-colocate-uniform':
                    for placement_num_hosts_per_leaf in [12, 24, 48]:
                        run_cloud([NUM_PODS,
                                   NUM_LEAFS_PER_POD,
                                   NUM_HOSTS_PER_LEAF,
                                   MAX_VMS_PER_HOST,
                                   NUM_TENANTS,
                                   MIN_VMS_PER_TENANT,
                                   MAX_VMS_PER_TENANT,
                                   VM_DIST,
                                   NUM_GROUPS,
                                   MIN_GROUP_SIZE,
                                   group_size_dist,
                                   placement_dist,
                                   placement_num_hosts_per_leaf,
                                   MULTI_THREADED,
                                   NUM_JOBS,
                                   seed,
                                   DUMP_FILE_PREFIX])
                elif placement_dist == 'colocate-uniform':
                    run_cloud([NUM_PODS,
                               NUM_LEAFS_PER_POD,
                               NUM_HOSTS_PER_LEAF,
                               MAX_VMS_PER_HOST,
                               NUM_TENANTS,
                               MIN_VMS_PER_TENANT,
                               MAX_VMS_PER_TENANT,
                               VM_DIST,
                               NUM_GROUPS,
                               MIN_GROUP_SIZE,
                               group_size_dist,
                               placement_dist,
                               -1,
                               MULTI_THREADED,
                               NUM_JOBS,
                               seed,
                               DUMP_FILE_PREFIX])
                else:
                    raise Exception('invalid placement_dist value')


def run_with_args(seed, group_size_dist, placement_dist, placement_num_hosts_per_leaf):
    run_cloud([NUM_PODS,
               NUM_LEAFS_PER_POD,
               NUM_HOSTS_PER_LEAF,
               MAX_VMS_PER_HOST,
               NUM_TENANTS,
               MIN_VMS_PER_TENANT,
               MAX_VMS_PER_TENANT,
               VM_DIST,
               NUM_GROUPS,
               MIN_GROUP_SIZE,
               group_size_dist,
               placement_dist,
               placement_num_hosts_per_leaf,
               MULTI_THREADED,
               NUM_JOBS,
               seed,
               DUMP_FILE_PREFIX])
