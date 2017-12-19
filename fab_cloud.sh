#!/usr/bin/env bash

for seed in 0 1 2
do
    for group_size_dist in "uniform" "wve"
    do
        for placement_dist in "colocate-colocate-uniform"
        do
            for placement_num_hosts_per_leaf in 12 24 48
            do
                fab -f fab_cloud.py \
                       run_with_args:${seed},${group_size_dist},${placement_dist},${placement_num_hosts_per_leaf} &
            done
        done
        wait

        for placement_dist in "colocate-uniform"
        do
            fab -f fab_cloud.py run_with_args:${seed},${group_size_dist},${placement_dist},-1 &
        done
        wait
     done
done
