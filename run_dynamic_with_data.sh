#!/usr/bin/env bash

# default parameters

NUM_EVENTS=1000000
DATA_FILE_PREFIX="/mnt/sdb1/baseerat/numerical-evals/12-4-2017/output-100K-random/optimizer.*"
LOG_FILE_PREFIX="/mnt/sdb1/baseerat/numerical-evals/12-4-2017/logs-100K-random/dynamic-logs"

PYTHON=pypy3  # options: pypy3 or python or python3

# running parameters

for file in ${DATA_FILE_PREFIX}
do
    ${PYTHON} run_dynamic.py  ${NUM_EVENTS} \
                              ${file} \
                              ${LOG_FILE_PREFIX} &
    wait
done
wait
