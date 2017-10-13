#!/usr/bin/env bash

#!/usr/bin/env bash

# default parameters

NUM_LEAFS=1056
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
PLACEMENT_DIST="colocate-linear"  # options: uniform, colocate-linear, and colocate-random
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


#TEST_NAME="baseerat"
#NUM_GROUPS=1000000
#
#for seed in 0 1 2 3 4
#do
#    for num_bitmaps in 10 20 30
#    do
#        for num_colocate_hosts in 20 30 48
#        do
#            python main.py ${TEST_NAME} ${seed} ${num_bitmaps} ${NUM_GROUPS} ${num_colocate_hosts} ./logs
#            echo
#        done
#    done
#done
