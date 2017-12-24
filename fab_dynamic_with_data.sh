#!/usr/bin/env bash

DATA_FILE_PREFIX="/mnt/sdb1/baseerat/numerical-evals/12-24-2017/output-1M/optimizer.*_leafs"

declare -i i=1
for file in ${DATA_FILE_PREFIX}
do
    fab -f fab_dynamic_with_data.py run_with_args:${file} &

    n=$((i%2))
    if [ ${n} -eq 0 ]
    then
        wait
    fi
    i=$((i+1))
done
