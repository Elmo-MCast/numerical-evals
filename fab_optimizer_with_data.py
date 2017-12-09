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
LOG_CLOUD_STATS = True
DATA_FILE_PREFIX = '/mnt/sdb1/baseerat/numerical-evals/12-9-2017/output-100K-random/cloud.*'
LOG_FILE_PREFIX = '/mnt/sdb1/baseerat/numerical-evals/12-9-2017/logs-100K-uniform/logs'

PYTHON = 'pypy3'  # options: pypy3 or python or python3


def run_optimizer_with_data(params):
    local('%s run_optimizer_with_data.py %s' % (PYTHON, ' '.join(map(str, params))))


def test():
    DATA_FILE_PREFIX = 'output/cloud.*'
    LOG_FILE_PREFIX = 'output/logs'

    files = glob(DATA_FILE_PREFIX)
    for file in files:
        run_optimizer_with_data([ALGORITHM,
                                 NUM_BITMAPS,
                                 NUM_NODES_PER_BITMAP,
                                 REDUNDANCY_PER_BITMAP,
                                 NUM_RULES,
                                 PROBABILITY_DIVIDEND,
                                 PROBABILITY_DIVISOR,
                                 NODE_TYPE,
                                 LOG_CLOUD_STATS,
                                 file,
                                 LOG_FILE_PREFIX])


def run_pods():
    NOTE_TYPE = 'pods'

    files = glob(DATA_FILE_PREFIX)
    for file in files:
        for num_rules in [10000, 64000]:
            for num_bitmaps in [1, 2, 3]:
                for num_nodes_per_bitmap in [3]:
                    run_optimizer_with_data(['exact-match',
                                             num_bitmaps,
                                             num_nodes_per_bitmap,
                                             0,
                                             num_rules,
                                             PROBABILITY_DIVIDEND,
                                             PROBABILITY_DIVISOR,
                                             NOTE_TYPE,
                                             LOG_CLOUD_STATS,
                                             file,
                                             LOG_FILE_PREFIX])

                    for redundancy_per_bitmap in [0, 6, 12, 24, 48]:
                        run_optimizer_with_data(['random-fuzzy-match',
                                                 num_bitmaps,
                                                 num_nodes_per_bitmap,
                                                 redundancy_per_bitmap,
                                                 num_rules,
                                                 PROBABILITY_DIVIDEND,
                                                 PROBABILITY_DIVISOR,
                                                 NOTE_TYPE,
                                                 LOG_CLOUD_STATS,
                                                 file,
                                                 LOG_FILE_PREFIX])


def run_leafs():
    NOTE_TYPE = 'leafs'

    files = glob(DATA_FILE_PREFIX)
    for file in files:
        for num_rules in [10000, 64000]:
            for num_bitmaps in [10, 20, 30]:
                for num_nodes_per_bitmap in [3]:
                    run_optimizer_with_data(['exact-match',
                                             num_bitmaps,
                                             num_nodes_per_bitmap,
                                             0,
                                             num_rules,
                                             PROBABILITY_DIVIDEND,
                                             PROBABILITY_DIVISOR,
                                             NOTE_TYPE,
                                             LOG_CLOUD_STATS,
                                             file,
                                             LOG_FILE_PREFIX])

                    for redundancy_per_bitmap in [0, 6, 12, 24, 48]:
                        run_optimizer_with_data(['random-fuzzy-match',
                                                 num_bitmaps,
                                                 num_nodes_per_bitmap,
                                                 redundancy_per_bitmap,
                                                 num_rules,
                                                 PROBABILITY_DIVIDEND,
                                                 PROBABILITY_DIVISOR,
                                                 NOTE_TYPE,
                                                 LOG_CLOUD_STATS,
                                                 file,
                                                 LOG_FILE_PREFIX])
