#!/usr/bin/env bash

TEST_NAME="baseerat"
NUM_GROUPS=100000

for seed in 0 1 2 3 4
do
    for num_bitmaps in 10 20 30
    do
        for num_colocate_hosts in 20 30 48
        do
            python main.py ${TEST_NAME} ${seed} ${num_bitmaps} ${NUM_GROUPS} ${num_colocate_hosts} ./logs
            echo
        done
    done
done
