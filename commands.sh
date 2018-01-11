#!/usr/bin/env bash

fab -f fab_cloud.py test_large
fab -f fab_optimizer.py test_pods_large test_leafs_large

fab -f fab_data.py test

fab -f fab_dynamic_with_data.py test_large
