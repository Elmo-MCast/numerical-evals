#!/usr/bin/env bash

DATA_FILE_PREFIX="/mnt/sdc1/baseerat/numerical-evals/1-26-2018/output-1M/cloud.12_48_48_20_3000_10_5000_expon_1000000_5_uniform_colocate-uniform_-1_True_5_2"
NODE_TYPE="pods"

declare -i i=1
for file in ${DATA_FILE_PREFIX}
do
#    for num_rules in 10000 64000
    for num_rules in 64000
    do
#        for num_bitmaps in 1 2 3
        for num_bitmaps in 2
        do
            for num_nodes_per_bitmap in 3
            do
#                fab -f fab_optimizer.py \
#                       run_with_args:${NODE_TYPE},${file},${num_rules},${num_bitmaps},${num_nodes_per_bitmap},0,"exact-match" &
#                fab -f fab_optimizer.py \
#                           run_with_args:${NODE_TYPE},${file},${num_rules},${num_bitmaps},${num_nodes_per_bitmap},0,"random-fuzzy-match" &
#                wait

                fab -f fab_optimizer.py \
                           run_with_args:${NODE_TYPE},${file},${num_rules},${num_bitmaps},${num_nodes_per_bitmap},6,"random-fuzzy-match" &
#                fab -f fab_optimizer.py \
#                           run_with_args:${NODE_TYPE},${file},${num_rules},${num_bitmaps},${num_nodes_per_bitmap},12,"random-fuzzy-match" &
#                wait
            done
#            wait
        done
    done

    n=$((i%3))
    if [ ${n} -eq 0 ]
    then
        wait
    fi
    i=$((i+1))
done


#DATA_FILE_PREFIX="/mnt/sdb1/baseerat/numerical-evals/12-11-2017/output-1M/optimizer.*random-fuzzy-match_2_3_6_64000_2_3_pods"
#NODE_TYPE="leafs"
#
#for file in ${DATA_FILE_PREFIX}
#do
#    for num_rules in 10000 64000
#    do
#        for num_bitmaps in 10 20 30
#        do
#            for num_nodes_per_bitmap in 3
#            do
#                fab -f fab_optimizer.py \
#                       run_with_args:${NODE_TYPE},${file},${num_rules},${num_bitmaps},${num_nodes_per_bitmap},0,"exact-match" &
#
#                for redundancy_per_bitmap in 0
#                do
#                    fab -f fab_optimizer.py \
#                           run_with_args:${NODE_TYPE},${file},${num_rules},${num_bitmaps},${num_nodes_per_bitmap},${redundancy_per_bitmap},"random-fuzzy-match" &
#                done
#                wait
#
#                for redundancy_per_bitmap in 6 12
#                do
#                    fab -f fab_optimizer.py \
#                           run_with_args:${NODE_TYPE},${file},${num_rules},${num_bitmaps},${num_nodes_per_bitmap},${redundancy_per_bitmap},"random-fuzzy-match" &
#                done
#                wait
#
#                for redundancy_per_bitmap in 24 48
#                do
#                    fab -f fab_optimizer.py \
#                           run_with_args:${NODE_TYPE},${file},${num_rules},${num_bitmaps},${num_nodes_per_bitmap},${redundancy_per_bitmap},"random-fuzzy-match" &
#                done
#                wait
#            done
#        done
#    done
#done

#DATA_FILE_PREFIX="/mnt/sdb1/baseerat/numerical-evals/1-25-2018/output-1M/optimizer.*_pods"
#NODE_TYPE="leafs"
#
#for file in ${DATA_FILE_PREFIX}
#do
#    for num_rules in 64000
#    do
#        for num_bitmaps in 30
#        do
#            for num_nodes_per_bitmap in 3
#            do
##                fab -f fab_optimizer.py \
##                       run_with_args:${NODE_TYPE},${file},${num_rules},${num_bitmaps},${num_nodes_per_bitmap},0,"exact-match" &
#
#                for redundancy_per_bitmap in 12
#                do
#                    fab -f fab_optimizer.py \
#                           run_with_args:${NODE_TYPE},${file},${num_rules},${num_bitmaps},${num_nodes_per_bitmap},${redundancy_per_bitmap},"random-fuzzy-match" &
#                done
##                wait
#            done
#        done
#    done
#done
