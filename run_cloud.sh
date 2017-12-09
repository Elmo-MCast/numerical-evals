#!/usr/bin/env bash

# default parameters

NUM_PODS=11
NUM_LEAFS_PER_POD=48
NUM_HOSTS_PER_LEAF=48
MAX_VMS_PER_HOST=20
NUM_TENANTS=3000
MIN_VMS_PER_TENANT=10
MAX_VMS_PER_TENANT=5000
VM_DIST="expon"  # options: expon
NUM_GROUPS=100000
MIN_GROUP_SIZE=5
GROUP_SIZE_DIST="uniform"  # options: uniform and wve
MULTI_THREADED="True"
NUM_JOBS=5
SEED=0
DUMP_FILE_PREFIX="/mnt/sdb1/baseerat/numerical-evals/12-9-2017/output-100K-random/cloud"

PYTHON=pypy3  # options: pypy3 or python or python3

# running parameters

for seed in 0 1 2
do
    for group_size_dist in "uniform" "wve"
    do
        ${PYTHON} run_cloud.py  ${NUM_PODS} \
                                ${NUM_LEAFS_PER_POD} \
                                ${NUM_HOSTS_PER_LEAF} \
                                ${MAX_VMS_PER_HOST} \
                                ${NUM_TENANTS} \
                                ${MIN_VMS_PER_TENANT} \
                                ${MAX_VMS_PER_TENANT} \
                                ${VM_DIST} \
                                ${NUM_GROUPS} \
                                ${MIN_GROUP_SIZE} \
                                ${group_size_dist} \
                                ${MULTI_THREADED} \
                                ${NUM_JOBS} \
                                ${seed} \
                                ${DUMP_FILE_PREFIX} &
    done
    wait
done
wait
