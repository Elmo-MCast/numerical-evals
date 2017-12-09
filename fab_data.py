from fabric.api import *
from glob import glob

LOG_CLOUD_STATS="True"
DATA_FILE_PREFIX="/mnt/sdb1/baseerat/numerical-evals/output/optimizer.*"
LOG_DIR="/mnt/sdb1/baseerat/numerical-evals/logs"

PYTHON = 'pypy3'  # options: pypy3 or python or python3


def run_data(params):
    local('%s run_data.py %s' % (PYTHON, ' '.join(map(str, params))))


def test():
    DATA_FILE_PREFIX = 'output/optimizer.*'
    LOG_DIR = 'output/logs'

    files = glob(DATA_FILE_PREFIX)
    for file in files:
        run_data([LOG_CLOUD_STATS, file, LOG_DIR])
