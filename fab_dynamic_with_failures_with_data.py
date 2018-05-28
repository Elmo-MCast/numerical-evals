from fabric.api import *
from glob import glob

NUM_EVENTS = 10000
FAILED_NODE_TYPE = 'spine'
NUM_SPINES_PER_POD = 4
DATA_FILE_PREFIX = "/mnt/sdb1/baseerat/numerical-evals/1-25-2018/output-1M/optimizer.*_leafs_*"
LOG_FILE_PREFIX = "/mnt/sdb1/baseerat/numerical-evals/5-28-2018/logs-1M/dynamic-logs"

PYTHON = 'pypy3'  # options: pypy3 or python or python3


def run_dynamic_with_failures_with_data(params):
    local('%s run_dynamic_with_failures_with_data.py %s' % (PYTHON, ' '.join(map(str, params))))


def kill():
    local('pkill -f run_dynamic_with_failures_with_data')


def test_spines():
    NUM_EVENTS = 10000
    FAILED_NODE_TYPE = 'spine'
    NUM_SPINES_PER_POD = 4
    DATA_FILE_PREFIX = 'output/optimizer.*_pods.*_leafs'
    LOG_FILE_PREFIX = 'output/dynamic-logs'

    files = glob(DATA_FILE_PREFIX)
    for file in files:
        run_dynamic_with_failures_with_data([NUM_EVENTS, FAILED_NODE_TYPE, NUM_SPINES_PER_POD, file, LOG_FILE_PREFIX])


def test_cores():
    NUM_EVENTS = 10000
    FAILED_NODE_TYPE = 'core'
    NUM_SPINES_PER_POD = 4
    DATA_FILE_PREFIX = 'output/optimizer.*_pods.*_leafs'
    LOG_FILE_PREFIX = 'output/dynamic-logs'

    files = glob(DATA_FILE_PREFIX)
    for file in files:
        run_dynamic_with_failures_with_data([NUM_EVENTS, FAILED_NODE_TYPE, NUM_SPINES_PER_POD, file, LOG_FILE_PREFIX])


def run_with_args(failed_node_type, file):
    run_dynamic_with_failures_with_data([NUM_EVENTS, failed_node_type, NUM_SPINES_PER_POD, file, LOG_FILE_PREFIX])
