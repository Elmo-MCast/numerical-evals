#!/usr/bin/env bash

# default parameters

MAX_BATCH_SIZE=1
ALGORITHM="single_match"
NUM_LEAFS_PER_BITMAP=3
REDUNDANCY_PER_BITMAP=2
DATA_FILE_PREFIX="output/cloud.pkl.*"
DUMP_FILE_PREFIX="output/optimizer.pkl"

PYTHON=python3  # options: pypy3 or python or python3

# running parameters

#${PYTHON} run_optimizer.py  ${MAX_BATCH_SIZE} \
#                            ${ALGORITHM} \
#                            ${NUM_LEAFS_PER_BITMAP} \
#                            ${REDUNDANCY_PER_BITMAP} \
#                            ${DATA_FILE} \
#                            ${DUMP_FILE_PREFIX}


for file in ${DATA_FILE_PREFIX}
do
    ${PYTHON} run_optimizer.py  ${MAX_BATCH_SIZE} \
                                "single_match" \
                                0 \
                                0 \
                                ${file} \
                                ${DUMP_FILE_PREFIX} &

    for num_leafs_per_bitmap in 1 2 3
    do
        ${PYTHON} run_optimizer.py  ${MAX_BATCH_SIZE} \
                                    "exact_match" \
                                    ${num_leafs_per_bitmap} \
                                    0 \
                                    ${file} \
                                    ${DUMP_FILE_PREFIX} &

        for redundancy_per_bitmap in 0 1 2
        do
            ${PYTHON} run_optimizer.py  ${MAX_BATCH_SIZE} \
                                        "greedy_match" \
                                        ${num_leafs_per_bitmap} \
                                        ${redundancy_per_bitmap} \
                                        ${file} \
                                        ${DUMP_FILE_PREFIX} &
        done
        wait
    done
done

