#!/usr/bin/env bash

# default parameters

NUM_LEAFS=576
NUM_HOSTS_PER_LEAF=48
NUM_RULES_PER_LEAF=6400
MAX_VMS_PER_HOST=20
NUM_TENANTS=3000
MIN_VMS_PER_TENANT=10
MAX_VMS_PER_TENANT=5000
VM_DIST="expon"  # options: expon
NUM_GROUPS=100000
MIN_GROUP_SIZE=5
GROUP_SIZE_DIST="uniform"  # options: uniform and wve
PLACEMENT_DIST="colocate-random-linear"  # options: uniform, colocate-random-linear,
# colocate-random-random, sorted-colocate-random-linear, and sorted-colocate-random-random
COLOCATE_NUM_HOSTS_PER_LEAF=48
NUM_BITMAPS=10
MULTI_THREADED="True"
NUM_JOBS=5
SEED=0
DUMP_FILE_PREFIX="output/cloud.pkl"

PYTHON=python3  # options: pypy3 or python or python3

# running parameters

#${PYTHON} run_cloud.py  ${NUM_LEAFS} \
#                        ${NUM_HOSTS_PER_LEAF} \
#                        ${NUM_RULES_PER_LEAF} \
#                        ${MAX_VMS_PER_HOST} \
#                        ${NUM_TENANTS} \
#                        ${MIN_VMS_PER_TENANT} \
#                        ${MAX_VMS_PER_TENANT} \
#                        ${VM_DIST} \
#                        ${NUM_GROUPS} \
#                        ${MIN_GROUP_SIZE} \
#                        ${GROUP_SIZE_DIST} \
#                        ${PLACEMENT_DIST} \
#                        ${COLOCATE_NUM_HOSTS_PER_LEAF} \
#                        ${NUM_BITMAPS} \
#                        ${MULTI_THREADED} \
#                        ${NUM_JOBS} \
#                        ${SEED} \
#                        ${DUMP_FILE_PREFIX}

for seed in 0 1
do
    for group_size_dist in "uniform" "wve"
    do
        for placement_dist in "colocate-random-linear"
        do
            for num_bitmaps in 10 20 30
            do
                for num_colocate_hosts in 24 48
                do
                    ${PYTHON} run_cloud.py  ${NUM_LEAFS} \
                                            ${NUM_HOSTS_PER_LEAF} \
                                            ${NUM_RULES_PER_LEAF} \
                                            ${MAX_VMS_PER_HOST} \
                                            ${NUM_TENANTS} \
                                            ${MIN_VMS_PER_TENANT} \
                                            ${MAX_VMS_PER_TENANT} \
                                            ${VM_DIST} \
                                            ${NUM_GROUPS} \
                                            ${MIN_GROUP_SIZE} \
                                            ${group_size_dist} \
                                            ${placement_dist} \
                                            ${num_colocate_hosts} \
                                            ${num_bitmaps} \
                                            ${MULTI_THREADED} \
                                            ${NUM_JOBS} \
                                            ${seed} \
                                            ${DUMP_FILE_PREFIX} &
                done
            done
            wait
        done
    done
done

