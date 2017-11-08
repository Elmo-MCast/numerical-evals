#!/usr/bin/env bash

# default parameters

MAX_BATCH_SIZE=1
ALGORITHM="single_match"
NUM_BITMAPS=10
NUM_LEAFS_PER_BITMAP=3
REDUNDANCY_PER_BITMAP=2
NUM_RULES_PER_LEAF=6400
DATA_FILE_PREFIX="output/cloud.pkl.*"
DUMP_FILE_PREFIX="output/optimizer.pkl"

PYTHON=python3  # options: pypy3 or python or python3

# running parameters

for file in ${DATA_FILE_PREFIX}
do
    for num_bitmaps in 10
    do
        ${PYTHON} run_optimizer.py  ${MAX_BATCH_SIZE} \
                                    "single-match" \
                                    ${num_bitmaps} \
                                    0 \
                                    0 \
                                    ${NUM_RULES_PER_LEAF} \
                                    ${file} \
                                    ${DUMP_FILE_PREFIX} &

        for num_leafs_per_bitmap in 1
        do
            ${PYTHON} run_optimizer.py  ${MAX_BATCH_SIZE} \
                                        "exact-match" \
                                        ${num_bitmaps} \
                                        ${num_leafs_per_bitmap} \
                                        0 \
                                        ${NUM_RULES_PER_LEAF} \
                                        ${file} \
                                        ${DUMP_FILE_PREFIX} &

            for redundancy_per_bitmap in 0
            do
                ${PYTHON} run_optimizer.py  ${MAX_BATCH_SIZE} \
                                            "greedy-match" \
                                            ${num_bitmaps} \
                                            ${num_leafs_per_bitmap} \
                                            ${redundancy_per_bitmap} \
                                            ${NUM_RULES_PER_LEAF} \
                                            ${file} \
                                            ${DUMP_FILE_PREFIX} &
            done
            wait
        done
    done
done

