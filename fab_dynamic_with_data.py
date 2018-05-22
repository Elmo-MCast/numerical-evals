from fabric.api import *
from glob import glob

NUM_EVENTS = 1000000
DATA_FILE_PREFIX = "/mnt/sdb1/baseerat/numerical-evals/1-25-2018/output-1M/optimizer.*_leafs_*"
LOG_FILE_PREFIX = "/mnt/sdb1/baseerat/numerical-evals/5-22-2018/logs-1M/dynamic-logs"

PYTHON = 'pypy3'  # options: pypy3 or python or python3


def run_dynamic_with_data(params):
    local('%s run_dynamic_with_data.py %s' % (PYTHON, ' '.join(map(str, params))))


def kill():
    local('pkill -f run_dynamic_with_data')


def test_small():
    NUM_EVENTS = 10000
    DATA_FILE_PREFIX = 'output/optimizer.*_pods.*_leafs'
    LOG_FILE_PREFIX = 'output/dynamic-logs'

    files = glob(DATA_FILE_PREFIX)
    for file in files:
        run_dynamic_with_data([NUM_EVENTS, file, LOG_FILE_PREFIX])


def test_large():
    NUM_EVENTS = 1000000
    DATA_FILE_PREFIX = 'output/optimizer.*_pods.*_leafs'
    LOG_FILE_PREFIX = 'output/dynamic-logs'

    files = glob(DATA_FILE_PREFIX)
    for file in files:
        run_dynamic_with_data([NUM_EVENTS, file, LOG_FILE_PREFIX])


def run_with_args(file):
    run_dynamic_with_data([NUM_EVENTS, file, LOG_FILE_PREFIX])