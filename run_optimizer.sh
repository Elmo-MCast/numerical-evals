#!/usr/bin/env bash

# default parameters

MAX_BATCH_SIZE=1
ALGORITHM="single_match"
NUM_BITMAPS=10
NUM_LEAFS_PER_BITMAP=3
REDUNDANCY_PER_BITMAP=2
NUM_RULES_PER_LEAF=10000
PROBABILITY_DIVIDEND=2
PROBABILITY_DIVISOR=3
DATA_FILE_PREFIX="/mnt/sdb1/baseerat/numerical-evals/output-1M/cloud.pkl.*"
DUMP_FILE_PREFIX="/mnt/sdb1/baseerat/numerical-evals/output-1M/optimizer.pkl"

PYTHON=pypy3  # options: pypy3 or python or python3

# running parameters

for file in ${DATA_FILE_PREFIX}
do
    for num_bitmaps in 30
    do
        ${PYTHON} run_optimizer.py  ${MAX_BATCH_SIZE} \
                                    "single-match" \
                                    ${num_bitmaps} \
                                    0 \
                                    0 \
                                    ${NUM_RULES_PER_LEAF} \
                                    ${PROBABILITY_DIVIDEND} \
                                    ${PROBABILITY_DIVISOR} \
                                    ${file} \
                                    ${DUMP_FILE_PREFIX} &

#        for num_leafs_per_bitmap in 4
#        do
#            ${PYTHON} run_optimizer.py  ${MAX_BATCH_SIZE} \
#                                        "exact-match" \
#                                        ${num_bitmaps} \
#                                        ${num_leafs_per_bitmap} \
#                                        0 \
#                                        ${NUM_RULES_PER_LEAF} \
#                                        ${PROBABILITY_DIVIDEND} \
#                                        ${PROBABILITY_DIVISOR} \
#                                        ${file} \
#                                        ${DUMP_FILE_PREFIX} &

#            for redundancy_per_bitmap in 0 2 4
#            do
#                ${PYTHON} run_optimizer.py  ${MAX_BATCH_SIZE} \
#                                            "greedy-match" \
#                                            ${num_bitmaps} \
#                                            ${num_leafs_per_bitmap} \
#                                            ${redundancy_per_bitmap} \
#                                            ${NUM_RULES_PER_LEAF} \
#                                            ${PROBABILITY_DIVIDEND} \
#                                            ${PROBABILITY_DIVISOR} \
#                                            ${file} \
#                                            ${DUMP_FILE_PREFIX} &

#                ${PYTHON} run_optimizer.py  ${MAX_BATCH_SIZE} \
#                                            "fuzzy-match" \
#                                            ${num_bitmaps} \
#                                            ${num_leafs_per_bitmap} \
#                                            ${redundancy_per_bitmap} \
#                                            ${NUM_RULES_PER_LEAF} \
#                                            ${PROBABILITY_DIVIDEND} \
#                                            ${PROBABILITY_DIVISOR} \
#                                            ${file} \
#                                            ${DUMP_FILE_PREFIX} &
#
#                ${PYTHON} run_optimizer.py  ${MAX_BATCH_SIZE} \
#                                            "random-fuzzy-match" \
#                                            ${num_bitmaps} \
#                                            ${num_leafs_per_bitmap} \
#                                            ${redundancy_per_bitmap} \
#                                            ${NUM_RULES_PER_LEAF} \
#                                            ${PROBABILITY_DIVIDEND} \
#                                            ${PROBABILITY_DIVISOR} \
#                                            ${file} \
#                                            ${DUMP_FILE_PREFIX} &
#            done
#            wait
#        done
    done
done
wait
