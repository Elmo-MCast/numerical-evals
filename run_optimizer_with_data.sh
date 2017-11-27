#!/usr/bin/env bash

# default parameters

MAX_BATCH_SIZE=1
ALGORITHM="single_match"
NUM_BITMAPS=10
NUM_LEAFS_PER_BITMAP=3
REDUNDANCY_PER_BITMAP=2
NUM_RULES_PER_LEAF=1000
PROBABILITY_DIVIDEND=2
PROBABILITY_DIVISOR=3
DATA_FILE_PREFIX="/mnt/sdb1/baseerat/numerical-evals/11-24-2017/output-100K-uniform/cloud.pkl.*"
LOG_FILE_PREFIX="/mnt/sdb1/baseerat/numerical-evals/11-24-2017/logs-100K-uniform/logs"

PYTHON=pypy3  # options: pypy3 or python or python3

# running parameters

for file in ${DATA_FILE_PREFIX}
do
    for num_rules_per_leaf in 1000 10000
    do
        for num_bitmaps in 10 20 30
        do
#            ${PYTHON} run_optimizer_with_data.py    ${MAX_BATCH_SIZE} \
#                                                    "single-match" \
#                                                    ${num_bitmaps} \
#                                                    1 \
#                                                    0 \
#                                                    ${num_rules_per_leaf} \
#                                                    ${PROBABILITY_DIVIDEND} \
#                                                    ${PROBABILITY_DIVISOR} \
#                                                    ${file} \
#                                                    ${LOG_FILE_PREFIX} &
#
##            wait
#
#            ${PYTHON} run_optimizer_with_data.py    ${MAX_BATCH_SIZE} \
#                                                    "random-single-match" \
#                                                    ${num_bitmaps} \
#                                                    1 \
#                                                    0 \
#                                                    ${num_rules_per_leaf} \
#                                                    ${PROBABILITY_DIVIDEND} \
#                                                    ${PROBABILITY_DIVISOR} \
#                                                    ${file} \
#                                                    ${LOG_FILE_PREFIX} &
##            wait

            for num_leafs_per_bitmap in 3
            do
                ${PYTHON} run_optimizer_with_data.py    ${MAX_BATCH_SIZE} \
                                                        "exact-match" \
                                                        ${num_bitmaps} \
                                                        ${num_leafs_per_bitmap} \
                                                        0 \
                                                        ${num_rules_per_leaf} \
                                                        ${PROBABILITY_DIVIDEND} \
                                                        ${PROBABILITY_DIVISOR} \
                                                        ${file} \
                                                        ${LOG_FILE_PREFIX} &
#                wait

                for redundancy_per_bitmap in 0 6 12 24 48 96
                do
#                    if [ ${num_leafs_per_bitmap} -eq 1 ] && [ ${redundancy_per_bitmap} -gt 0 ]
#                    then
#                        continue
#                    fi

                    ${PYTHON} run_optimizer_with_data.py    ${MAX_BATCH_SIZE} \
                                                            "fuzzy-match" \
                                                            ${num_bitmaps} \
                                                            ${num_leafs_per_bitmap} \
                                                            ${redundancy_per_bitmap} \
                                                            ${num_rules_per_leaf} \
                                                            ${PROBABILITY_DIVIDEND} \
                                                            ${PROBABILITY_DIVISOR} \
                                                            ${file} \
                                                            ${LOG_FILE_PREFIX} &
#                    wait

                    ${PYTHON} run_optimizer_with_data.py    ${MAX_BATCH_SIZE} \
                                                            "random-fuzzy-match" \
                                                            ${num_bitmaps} \
                                                            ${num_leafs_per_bitmap} \
                                                            ${redundancy_per_bitmap} \
                                                            ${num_rules_per_leaf} \
                                                            ${PROBABILITY_DIVIDEND} \
                                                            ${PROBABILITY_DIVISOR} \
                                                            ${file} \
                                                            ${LOG_FILE_PREFIX} &
#                    wait
                done
                wait
            done
        done
    done
done
wait
