#!/usr/bin/env bash

LOG_CLOUD_STATS="True"
DATA_FILE_PREFIX="/mnt/sdb1/baseerat/numerical-evals/12-11-2017/output-1M/optimizer.*"

declare -i i=1
for file in ${DATA_FILE_PREFIX}
do
    fab -f fab_data.py run_with_args:${file},${LOG_CLOUD_STATS} &

    n=$((i%3))
    if [ ${n} -eq 0 ]
    then
        wait
    fi
    i=$((i+1))
done

