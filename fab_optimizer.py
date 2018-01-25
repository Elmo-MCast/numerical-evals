from fabric.api import *
from glob import glob

ALGORITHM = 'random-fuzzy-match'
NUM_BITMAPS = 3
NUM_NODES_PER_BITMAP = 2
REDUNDANCY_PER_BITMAP = 6
NUM_RULES = 10000
PROBABILITY_DIVIDEND = 2
PROBABILITY_DIVISOR = 3
NODE_TYPE = 'pods'
DATA_FILE_PREFIX = '/mnt/sdb1/baseerat/numerical-evals/1-25-2018/output-1M/cloud.*'
DUMP_FILE_PREFIX = '/mnt/sdb1/baseerat/numerical-evals/1-25-2018/output-1M/optimizer'

PYTHON = 'pypy3'  # options: pypy3 or python or python3


def run_optimizer(params):
    local('%s run_optimizer.py %s' % (PYTHON, ' '.join(map(str, params))))


def kill():
    local('pkill -f run_optimizer')


def test_pods_small():
    ALGORITHM = 'random-fuzzy-match'
    NUM_BITMAPS = 1
    NUM_NODES_PER_BITMAP = 1
    REDUNDANCY_PER_BITMAP = 0
    NUM_RULES = 5
    PROBABILITY_DIVIDEND = 2
    PROBABILITY_DIVISOR = 3
    NODE_TYPE = 'pods'
    DATA_FILE_PREFIX = 'output/cloud.*'
    DUMP_FILE_PREFIX = 'output/optimizer'

    files = glob(DATA_FILE_PREFIX)
    for file in files:
        run_optimizer([ALGORITHM,
                       NUM_BITMAPS,
                       NUM_NODES_PER_BITMAP,
                       REDUNDANCY_PER_BITMAP,
                       NUM_RULES,
                       PROBABILITY_DIVIDEND,
                       PROBABILITY_DIVISOR,
                       NODE_TYPE,
                       file,
                       DUMP_FILE_PREFIX])


def test_leafs_small():
    ALGORITHM = 'random-fuzzy-match'
    NUM_BITMAPS = 5
    NUM_NODES_PER_BITMAP = 2
    REDUNDANCY_PER_BITMAP = 6
    NUM_RULES = 100
    PROBABILITY_DIVIDEND = 2
    PROBABILITY_DIVISOR = 3
    NODE_TYPE = 'leafs'
    DATA_FILE_PREFIX = 'output/optimizer.*'
    DUMP_FILE_PREFIX = 'output/optimizer'

    files = glob(DATA_FILE_PREFIX)
    for file in files:
        run_optimizer([ALGORITHM,
                       NUM_BITMAPS,
                       NUM_NODES_PER_BITMAP,
                       REDUNDANCY_PER_BITMAP,
                       NUM_RULES,
                       PROBABILITY_DIVIDEND,
                       PROBABILITY_DIVISOR,
                       NODE_TYPE,
                       file,
                       DUMP_FILE_PREFIX])


def test_pods_large():
    ALGORITHM = 'random-fuzzy-match'
    NUM_BITMAPS = 2
    NUM_NODES_PER_BITMAP = 3
    REDUNDANCY_PER_BITMAP = 6
    NUM_RULES = 1000
    PROBABILITY_DIVIDEND = 2
    PROBABILITY_DIVISOR = 3
    NODE_TYPE = 'pods'
    DATA_FILE_PREFIX = 'output/cloud.*'
    DUMP_FILE_PREFIX = 'output/optimizer'

    files = glob(DATA_FILE_PREFIX)
    for file in files:
        run_optimizer([ALGORITHM,
                       NUM_BITMAPS,
                       NUM_NODES_PER_BITMAP,
                       REDUNDANCY_PER_BITMAP,
                       NUM_RULES,
                       PROBABILITY_DIVIDEND,
                       PROBABILITY_DIVISOR,
                       NODE_TYPE,
                       file,
                       DUMP_FILE_PREFIX])


def test_leafs_large():
    ALGORITHM = 'random-fuzzy-match'
    NUM_BITMAPS = 10
    NUM_NODES_PER_BITMAP = 3
    REDUNDANCY_PER_BITMAP = 12
    NUM_RULES = 10000
    PROBABILITY_DIVIDEND = 2
    PROBABILITY_DIVISOR = 3
    NODE_TYPE = 'leafs'
    DATA_FILE_PREFIX = 'output/optimizer.*'
    DUMP_FILE_PREFIX = 'output/optimizer'

    files = glob(DATA_FILE_PREFIX)
    for file in files:
        run_optimizer([ALGORITHM,
                       NUM_BITMAPS,
                       NUM_NODES_PER_BITMAP,
                       REDUNDANCY_PER_BITMAP,
                       NUM_RULES,
                       PROBABILITY_DIVIDEND,
                       PROBABILITY_DIVISOR,
                       NODE_TYPE,
                       file,
                       DUMP_FILE_PREFIX])


def run_pods():
    NODE_TYPE = 'pods'

    files = glob(DATA_FILE_PREFIX)
    for file in files:
        for num_rules in [10000, 64000]:
            for num_bitmaps in [1, 2, 3]:
                for num_nodes_per_bitmap in [3]:
                    run_optimizer(['exact-match',
                                   num_bitmaps,
                                   num_nodes_per_bitmap,
                                   0,
                                   num_rules,
                                   PROBABILITY_DIVIDEND,
                                   PROBABILITY_DIVISOR,
                                   NODE_TYPE,
                                   file,
                                   DUMP_FILE_PREFIX])

                    for redundancy_per_bitmap in [0, 6, 12, 24, 48]:
                        run_optimizer(['random-fuzzy-match',
                                       num_bitmaps,
                                       num_nodes_per_bitmap,
                                       redundancy_per_bitmap,
                                       num_rules,
                                       PROBABILITY_DIVIDEND,
                                       PROBABILITY_DIVISOR,
                                       NODE_TYPE,
                                       file,
                                       DUMP_FILE_PREFIX])


def run_leafs():
    NODE_TYPE = 'leafs'

    files = glob(DATA_FILE_PREFIX)
    for file in files:
        for num_rules in [10000, 64000]:
            for num_bitmaps in [10, 20, 30]:
                for num_nodes_per_bitmap in [3]:
                    run_optimizer(['exact-match',
                                   num_bitmaps,
                                   num_nodes_per_bitmap,
                                   0,
                                   num_rules,
                                   PROBABILITY_DIVIDEND,
                                   PROBABILITY_DIVISOR,
                                   NODE_TYPE,
                                   file,
                                   DUMP_FILE_PREFIX])

                    for redundancy_per_bitmap in [0, 6, 12, 24, 48]:
                        run_optimizer(['random-fuzzy-match',
                                       num_bitmaps,
                                       num_nodes_per_bitmap,
                                       redundancy_per_bitmap,
                                       num_rules,
                                       PROBABILITY_DIVIDEND,
                                       PROBABILITY_DIVISOR,
                                       NODE_TYPE,
                                       file,
                                       DUMP_FILE_PREFIX])


def run_with_args(node_type, file, num_rules, num_bitmaps, num_nodes_per_bitmap, redundancy_per_bitmap, algorithm):
    run_optimizer([algorithm,
                   num_bitmaps,
                   num_nodes_per_bitmap,
                   redundancy_per_bitmap,
                   num_rules,
                   PROBABILITY_DIVIDEND,
                   PROBABILITY_DIVISOR,
                   node_type,
                   file,
                   DUMP_FILE_PREFIX])
