from timeit import default_timer as timer
import numpy as np
from simulation.algorithms import algorithms
from simulation.utils import bar_range


class Dynamic:
    def __init__(self, data):
        self.data = data

        self.tenants = self.data['tenants']
        self.tenants_maps = self.tenants['maps']

        self.optimizer = self.data['optimizer']
        self.leafs_to_rules_count = self.optimizer['leafs_to_rules_count']

        pass
