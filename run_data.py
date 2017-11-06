import sys
import random
from simulation.data import Data
from simulation.utils import load_obj, dump_obj

if len(sys.argv) > 1:
    DATA_FILE = sys.argv[5]
    SEED = int(sys.argv[7])
elif True:
    DATA_FILE = 'simulation/output/optimizer.pkl'
    SEED = 0
else:
    raise (Exception('invalid parameters'))

print("""
-> data ()
""")

random.seed(SEED)

data = load_obj(DATA_FILE)

data = Data(data)
