#!/usr/bin/env bash

for seed in 0 1 2 3 4
do
    python main.py ${seed} 10 ./logs
    python main.py ${seed} 20 ./logs
    python main.py ${seed} 30 ./logs
done
