#!/usr/bin/env bash

# default parameters

DATA_FILE_PREFIX="output/optimizer.pkl.*"
LOG_DIR="logs"

PYTHON=python3  # options: pypy3 or python or python3

# running parameters

for file in ${DATA_FILE_PREFIX}
do
    ${PYTHON} run_data.py ${file} \
                          ${LOG_DIR}
done

