from fabric.api import *
from glob import glob

NUM_EVENTS=10000
DATA_FILE_PREFIX="/mnt/sdb1/baseerat/numerical-evals/12-2-2017/output-1M-random/optimizer.*"
DUMP_FILE_PREFIX="/mnt/sdb1/baseerat/numerical-evals/12-2-2017/output-1M-random/dynamic"

PYTHON = 'pypy3'  # options: pypy3 or python or python3


def run_dynamic(params):
    local('%s run_dynamic.py %s' % (PYTHON, ' '.join(map(str, params))))


def kill():
    local('pkill -f run_dynamic')


def test():
    DATA_FILE_PREFIX = 'output/optimizer.*_pods.*_leafs'
    DUMP_FILE_PREFIX = 'output/dynamic'

    files = glob(DATA_FILE_PREFIX)
    for file in files:
        run_dynamic([NUM_EVENTS, file, DUMP_FILE_PREFIX])
