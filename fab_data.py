from fabric.api import *
from glob import glob

LOG_CLOUD_STATS="True"
NUM_CORES = 4
NUM_SPINES_PER_POD = 4
DATA_FILE_PREFIX="/mnt/sdb1/baseerat/numerical-evals/12-11-2017/output-1M/optimizer.*"
LOG_DIR="/mnt/sdb1/baseerat/numerical-evals/1-10-2018/logs-1M/logs"

PYTHON = 'pypy3'  # options: pypy3 or python or python3


def run_data(params):
    local('%s run_data.py %s' % (PYTHON, ' '.join(map(str, params))))


def kill():
    local('pkill -f run_data')


def test_pods():
    DATA_FILE_PREFIX = 'output/optimizer.*_pods'
    LOG_DIR = 'output/logs'
    NUM_CORES = 4
    NUM_SPINES_PER_POD = 4

    files = glob(DATA_FILE_PREFIX)
    for file in files:
        run_data([LOG_CLOUD_STATS, NUM_CORES, NUM_SPINES_PER_POD, file, LOG_DIR])


def test_leafs():
    LOG_CLOUD_STATS = "False"
    DATA_FILE_PREFIX = 'output/optimizer.*_leafs'
    LOG_DIR = 'output/logs'

    files = glob(DATA_FILE_PREFIX)
    for file in files:
        run_data([LOG_CLOUD_STATS, NUM_CORES, NUM_SPINES_PER_POD, file, LOG_DIR])


def test():
    DATA_FILE_PREFIX = 'output/optimizer.*_pods.*_leafs'
    LOG_DIR = 'output/logs'

    files = glob(DATA_FILE_PREFIX)
    for file in files:
        run_data([LOG_CLOUD_STATS, NUM_CORES, NUM_SPINES_PER_POD, file, LOG_DIR])


def run_with_args(file, log_cloud_stats='True', num_cores=4, num_spines_per_pod=4):
    run_data([True if log_cloud_stats == 'True' else False, num_cores, num_spines_per_pod, file, LOG_DIR])
