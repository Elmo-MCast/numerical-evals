#!/usr/bin/env bash

# default parameters

DATA_FILE_PREFIX="/mnt/sdb1/baseerat/numerical-evals/output/optimizer.*"
LOG_DIR="/mnt/sdb1/baseerat/numerical-evals/logs"

PYTHON=python3  # options: pypy3 or python or python3

# running parameters

for file in ${DATA_FILE_PREFIX}
do
    ${PYTHON} run_data.py ${file} \
                          ${LOG_DIR}
done
wait
