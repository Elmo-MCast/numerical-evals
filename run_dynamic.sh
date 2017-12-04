#!/usr/bin/env bash

# default parameters

NUM_EVENTS=10000
DATA_FILE_PREFIX="/mnt/sdb1/baseerat/numerical-evals/12-2-2017/output-1M-random/optimizer.*"
DUMP_FILE_PREFIX="/mnt/sdb1/baseerat/numerical-evals/12-2-2017/output-1M-random/dynamic"

PYTHON=pypy3  # options: pypy3 or python or python3

# running parameters

for file in ${DATA_FILE_PREFIX}
do
    ${PYTHON} run_dynamic.py  ${NUM_EVENTS} \
                              ${file} \
                              ${DUMP_FILE_PREFIX} &
    wait
done
wait
