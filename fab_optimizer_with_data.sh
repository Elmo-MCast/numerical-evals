#!/usr/bin/env bash

DATA_FILE_PREFIX="/mnt/sdb1/baseerat/numerical-evals/12-11-2017/output-1M/optimizer.*random-fuzzy-match_2_3_6_64000_2_3_pods"
NODE_TYPE="leafs"

for file in ${DATA_FILE_PREFIX}
do
    for num_rules in 10000 64000
    do
        for num_bitmaps in 10 20 30
        do
            for num_nodes_per_bitmap in 3
            do
                fab -f fab_optimizer_with_data.py \
                       run_with_args:${NODE_TYPE},${file},${num_rules},${num_bitmaps},${num_nodes_per_bitmap},0,"exact-match" &

                for redundancy_per_bitmap in 0
                do
                    fab -f fab_optimizer_with_data.py \
                           run_with_args:${NODE_TYPE},${file},${num_rules},${num_bitmaps},${num_nodes_per_bitmap},${redundancy_per_bitmap},"random-fuzzy-match" &
                done
                wait

                for redundancy_per_bitmap in 6 12
                do
                    fab -f fab_optimizer_with_data.py \
                           run_with_args:${NODE_TYPE},${file},${num_rules},${num_bitmaps},${num_nodes_per_bitmap},${redundancy_per_bitmap},"random-fuzzy-match" &
                done
                wait

                for redundancy_per_bitmap in 24 48
                do
                    fab -f fab_optimizer_with_data.py \
                           run_with_args:${NODE_TYPE},${file},${num_rules},${num_bitmaps},${num_nodes_per_bitmap},${redundancy_per_bitmap},"random-fuzzy-match" &
                done
                wait
            done
        done
    done
done
