import random
import pandas as pd
import multiprocessing
from joblib import Parallel, delayed
from simulation.utils import bar_range


def unwrap_tenant_groups_to_vms_map(args, **kwargs):
    return Tenants._get_tenant_groups_to_vms_map_mproc(*args, **kwargs)


class Tenants:
    def __init__(self, data, num_tenants=3000, min_vms=10, max_vms=5000, vm_dist='expon',
                 num_groups=100000, min_group_size=5, group_size_dist='uniform', debug=False,
                 multi_threaded=False, num_jobs=4):
        self.data = data
        self.num_tenants = num_tenants
        self.min_vms = min_vms
        self.max_vms = max_vms
        self.vm_dist = vm_dist
        self.num_groups = num_groups
        self.min_group_size = min_group_size
        self.group_size_dist = group_size_dist
        self.multi_threaded = multi_threaded
        self.num_jobs = num_jobs
        self.debug = debug

        self.data['tenants'] = {'vm_count': 0,
                                'group_count': 0,
                                'maps': [{'vm_count': None,
                                          'group_count': None,
                                          'groups_map': None} for _ in range(self.num_tenants)]
                                }

        self.tenants = self.data['tenants']
        self.tenants_maps = self.tenants['maps']

        self._get_tenant_to_vm_count_map()
        self._get_tenant_to_group_count_map()

        for t in range(self.num_tenants):
            tenant_maps = self.tenants_maps[t]
            tenant_maps['groups_map'] = \
                [{'size': None, 'vms': None} for _ in range(tenant_maps['group_count'])]

        self._get_tenant_groups_to_sizes_map()
        if not self.multi_threaded:
            self._get_tenant_groups_to_vms_map()
        else:
            self._run_tenant_groups_to_vms_map()

    def _get_tenant_to_vm_count_map(self):
        if self.vm_dist == 'expon':
            _vm_count = 0
            for t in bar_range(self.num_tenants, desc='tenants:vm count'):
                sample = random.random()
                if sample < 0.02:
                    vm_count = random.randint(self.min_vms, self.max_vms)
                else:
                    vm_count = int((random.expovariate(4.05) / 10) * (self.max_vms - self.min_vms)) \
                               % (self.max_vms - self.min_vms) + self.min_vms

                self.tenants_maps[t]['vm_count'] = vm_count
                _vm_count += vm_count
            self.tenants['vm_count'] = _vm_count
        else:
            raise (Exception("invalid dist parameter for vm allocation"))

        if self.debug:
            print(pd.Series([self.tenants_maps[t]['vm_count'] for t in range(self.num_tenants)]).describe())
            print("VM Count: %s" % self.tenants['vm_count'])

    def _get_tenant_to_group_count_map(self):
        # ... weighted assignment of groups (based on VMs) to tenants
        _vm_count = self.tenants['vm_count']
        _group_count = 0
        for t in bar_range(self.num_tenants, desc='tenants:group count'):
            tenant_maps = self.tenants_maps[t]
            group_count = int(tenant_maps['vm_count'] / _vm_count * self.num_groups)
            tenant_maps['group_count'] = group_count
            _group_count += group_count
        self.tenants['group_count'] = _group_count

        if self.debug:
            print(pd.Series([self.tenants_maps[t]['group_count'] for t in range(self.num_tenants)]).describe())
            print("Sum: %s" % sum(pd.Series([self.tenants_maps[t]['group_count'] for t in range(self.num_tenants)])))

    def _get_tenant_groups_to_sizes_map(self):
        if self.group_size_dist == 'uniform':
            for t in bar_range(self.num_tenants, desc='tenants:group sizes'):
                tenant_maps = self.tenants_maps[t]
                vm_count = tenant_maps['vm_count']
                group_count = tenant_maps['group_count']
                groups_map = tenant_maps['groups_map']
                for g in range(group_count):
                    size = random.randint(self.min_group_size, vm_count)
                    groups_map[g]['size'] = size
        elif self.group_size_dist == 'wve':  # ... using mix3 distribution from the dcn-mcast paper.
            for t in bar_range(self.num_tenants, desc='tenants:group sizes'):
                tenant_maps = self.tenants_maps[t]
                vm_count = tenant_maps['vm_count']
                group_count = tenant_maps['group_count']
                groups_map = tenant_maps['groups_map']
                for g in range(group_count):
                    sample = random.random()
                    if sample < 0.02:
                        size = vm_count - int(random.gammavariate(2, 0.1) * vm_count / 15) % vm_count
                    else:
                        size = int(random.gammavariate(2, 0.2) * vm_count / 15 + self.min_group_size - 1) % vm_count + 1
                    size = max(size, self.min_group_size)
                    groups_map[g]['size'] = size
        else:
            raise (Exception("invalid dist parameter for group size allocation"))

        if self.debug:
            _group_sizes_for_all_tenants = []
            for t in range(self.num_tenants):
                tenant_maps = self.tenants_maps[t]
                group_count = tenant_maps['group_count']
                groups_map = tenant_maps['groups_map']
                for g in range(group_count):
                    _group_sizes_for_all_tenants += [groups_map[g]['size']]
            print(pd.Series(_group_sizes_for_all_tenants).describe())

    def _get_tenant_groups_to_vms_map(self):
        for t in bar_range(self.num_tenants, desc='tenants:groups->vms'):
            tenant_maps = self.tenants_maps[t]
            vm_count = tenant_maps['vm_count']
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']
            for g in range(group_count):
                group_map = groups_map[g]
                group_map['vms'] = random.sample(range(vm_count), group_map['size'])

    @staticmethod
    def _get_tenant_groups_to_vms_map_mproc(tenants_maps, num_tenants):
        for t in bar_range(range(num_tenants), 'tenants:groups->vms'):
            tenant_maps = tenants_maps[t]
            vm_count = tenant_maps['vm_count']
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']
            for g in range(group_count):
                group_map = groups_map[g]
                group_map['vms'] = random.sample(range(vm_count), group_map['size'])
        return tenants_maps

    def _run_tenant_groups_to_vms_map(self):
        if (self.num_tenants % self.num_jobs) != 0:
            raise (Exception('input not divisible by num_jobs'))

        input_size = int(self.num_tenants / self.num_jobs)
        input_groups = [(i, i + input_size) for i in range(0, self.num_tenants, input_size)]
        inputs = [(self.tenants_maps[i:j],
                   input_size) for i, j in input_groups]

        # pool = multiprocessing.Pool()
        # results = pool.map(unwrap_tenant_groups_to_vms_map, [i for i in inputs])

        num_cpus = multiprocessing.cpu_count()
        Parallel(n_jobs=num_cpus, backend="threading")(
            delayed(unwrap_tenant_groups_to_vms_map)(i) for i in inputs)
