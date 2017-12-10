from fabric.api import *
from glob import glob

NUM_EVENTS=10000
DATA_FILE_PREFIX="/mnt/sdb1/baseerat/numerical-evals/12-2-2017/output-1M-random/optimizer.*"
LOG_FILE_PREFIX="/mnt/sdb1/baseerat/numerical-evals/12-2-2017/output-1M-random/dynamic"

PYTHON = 'pypy3'  # options: pypy3 or python or python3


def run_dynamic_with_data(params):
    local('%s run_dynamic_with_data.py %s' % (PYTHON, ' '.join(map(str, params))))


def kill():
    local('pkill -f run_dynamic_with_data')


def test():
    DATA_FILE_PREFIX = 'output/optimizer.*_pods.*_leafs'
    LOG_FILE_PREFIX = 'output/dynamic-logs'

    files = glob(DATA_FILE_PREFIX)
    for file in files:
        run_dynamic_with_data([NUM_EVENTS, file, LOG_FILE_PREFIX])
