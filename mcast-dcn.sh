#!/usr/bin/env bash

# default parameters

NUM_LEAFS=576
NUM_HOSTS_PER_LEAF=48
NUM_RULES_PER_LEAF=1000
MAX_VMS_PER_HOST=20
NUM_TENANTS=3000
MIN_VMS_PER_TENANT=10
MAX_VMS_PER_TENANT=5000
VM_DIST="expon"  # options: expon, expon-mean, and geom
NUM_GROUPS=100000
MIN_GROUP_SIZE=5
GROUP_SIZE_DIST="uniform"  # options: uniform and wve
PLACEMENT_DIST="colocate-random-linear"  # options: uniform, colocate-random-linear, and colocate-random-random
COLOCATE_NUM_HOSTS_PER_LEAF=48
NUM_BITMAPS=10
MAX_BATCH_SIZE=1
SEED=0
LOGS_DIR="./logs"

# running parameters

python main.py ${NUM_LEAFS} ${NUM_HOSTS_PER_LEAF} ${NUM_RULES_PER_LEAF} ${MAX_VMS_PER_HOST} ${NUM_TENANTS} \
               ${MIN_VMS_PER_TENANT} ${MAX_VMS_PER_TENANT} ${VM_DIST} ${NUM_GROUPS} ${MIN_GROUP_SIZE} \
               ${GROUP_SIZE_DIST} ${PLACEMENT_DIST} ${COLOCATE_NUM_HOSTS_PER_LEAF} ${NUM_BITMAPS} ${MAX_BATCH_SIZE} \
               ${SEED} ${LOGS_DIR}
