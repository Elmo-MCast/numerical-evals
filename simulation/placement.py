import numpy as np
import multiprocessing
from joblib import Parallel, delayed
from simulation.utils import bar_range, bar_tqdm


# def unwrap_tenant_groups_to_leafs_and_count_map(arg, **kwarg):
#     return Placement._get_tenant_groups_to_leafs_and_count_map(*arg, **kwarg)


def unwrap_tenant_groups_leafs_to_hosts_and_bitmap_map(arg, **kwarg):
    return Placement._get_tenant_groups_leafs_to_hosts_and_bitmap_map(*arg, **kwarg)


class Placement:
    def __init__(self, data, dist='uniform',  # options: uniform, colocate-random-linear, colocate-random-random
                 num_bitmaps=32, num_hosts_per_leaf=48, num_jobs=4):
        self.data = data
        self.dist = dist
        self.num_bitmaps = num_bitmaps
        self.num_hosts_per_leaf = num_hosts_per_leaf
        self.num_jobs = num_jobs

        self.network = self.data['network']
        self.network_maps = self.network['maps']

        self.num_leafs = self.network['num_leafs']
        self.num_hosts_per_leaf = self.network['num_hosts_per_leaf']

        self.tenants = self.data['tenants']
        self.tenants_maps = self.tenants['maps']

        self.num_hosts = self.tenants['num_hosts']
        self.num_tenants = self.tenants['num_tenants']
        self.max_vms_per_host = self.tenants['max_vms_per_host']

        self.data['placement'] = {'dist': self.dist,
                                  'num_bitmaps': self.num_bitmaps,
                                  'num_hosts_per_leaf': self.num_hosts_per_leaf,
                                  'maps': {
                                      'vm_to_host': [None] * self.num_tenants,
                                      'vm_to_leaf': [None] * self.num_tenants,
                                      'groups': [None] * self.num_tenants}}
        self.placement = self.data['placement']
        self.placement_maps = self.placement['maps']

        self._get_tenant_vms_to_host_map()
        print('placement:vms->host ... done')

        groups = self.placement_maps['groups']
        for t in range(self.num_tenants):
            groups[t] = {'leafs': None,
                         'leaf_counts': None,
                         'maps': {
                             'leafs': None}}

        # self._get_tenant_groups_to_leafs_and_count_map()
        # self._run_tenant_groups_to_leafs_and_count_map()
        # print('placement:groups->leafs ... done')

        # self._get_tenant_groups_leafs_to_hosts_and_bitmap_map()
        self._run_tenant_groups_leafs_to_hosts_and_bitmap_map()
        print('placement:groups->bitmap ... done')

    def _uniform(self):
        host_to_leaf = self.network_maps['host_to_leaf']
        vm_to_host = self.placement_maps['vm_to_host']
        vm_to_leaf = self.placement_maps['vm_to_leaf']
        available_hosts = np.array(range(self.num_hosts), dtype=int)
        available_hosts_count = np.zeros(shape=self.num_hosts, dtype=int)

        vm_counts = self.tenants_maps['vm_counts']
        for t in range(self.num_tenants):
            vm_count = vm_counts[t]

            hosts = np.random.choice(available_hosts, vm_count, replace=False)
            available_hosts_count[hosts] += 1
            vm_to_host[t] = hosts
            vm_to_leaf[t] = host_to_leaf[hosts]

            indexes = np.where(available_hosts_count == self.max_vms_per_host)
            for h in indexes[0]:
                available_hosts = np.delete(available_hosts, np.where(available_hosts == h))
            available_hosts_count[indexes] = -1

    def _colocate_random_linear(self, is_sorted=False, is_reverse=False):
        # if is_sorted:
        #     vm_counts = sorted(self.tenants_maps['vm_counts'], reverse=is_reverse)
        # else:
        #     vm_counts = self.tenants_maps['vm_counts']

        vm_counts = self.tenants_maps['vm_counts']
        vm_to_host_map = self.placement_maps['vm_to_host']
        vm_to_leaf_map = self.placement_maps['vm_to_leaf']
        available_leafs = np.array(range(self.num_leafs), dtype=int)
        available_hosts_per_leaf = [None] * self.num_leafs
        available_hosts_count_per_leaf = [None] * self.num_leafs

        available_hosts_per_leaf[0] = np.array(range(self.num_hosts_per_leaf))
        available_hosts_count_per_leaf[0] = np.zeros(shape=self.num_hosts_per_leaf, dtype=int)
        for l in range(1, self.num_leafs):
            available_hosts_per_leaf[l] = available_hosts_per_leaf[l - 1] + self.num_hosts_per_leaf
            available_hosts_count_per_leaf[l] = np.zeros(shape=self.num_hosts_per_leaf, dtype=int)

        for t in range(self.num_tenants):
            vm_count = vm_counts[t]
            vm_to_host = np.empty(shape=vm_count, dtype=int)
            vm_to_leaf = np.empty(shape=vm_count, dtype=int)

            running_index = 0
            running_count = vm_count
            while running_count > 0:
                selected_leaf = np.random.choice(available_leafs, 1, replace=False)[0]
                selected_hosts_per_leaf = available_hosts_per_leaf[selected_leaf]
                selected_hosts_count_per_leaf = available_hosts_count_per_leaf[selected_leaf]
                selected_leaf_hosts_count = len(selected_hosts_per_leaf)

                # to ensure that we always pick hosts <= self.placement['num_hosts_per_leaf'] at each leaf
                if selected_leaf_hosts_count > self.num_hosts_per_leaf:
                    selected_leaf_hosts_count = self.num_hosts_per_leaf

                if int(running_count / selected_leaf_hosts_count) > 0:
                    vm_to_host[running_index:running_index + selected_leaf_hosts_count] = \
                        selected_hosts_per_leaf[0:selected_leaf_hosts_count]
                    vm_to_leaf[running_index:running_index + selected_leaf_hosts_count] = selected_leaf
                    selected_hosts_count_per_leaf[0:selected_leaf_hosts_count] += 1
                    running_index += selected_leaf_hosts_count
                    running_count -= selected_leaf_hosts_count
                else:
                    vm_to_host[running_index:running_index + running_count] = \
                        selected_hosts_per_leaf[0:running_count]
                    vm_to_leaf[running_index:running_index + running_count] = selected_leaf
                    selected_hosts_count_per_leaf[0:running_count] += 1
                    running_index += running_count
                    running_count = 0

                indexes = np.where(selected_hosts_count_per_leaf == self.max_vms_per_host)
                if len(indexes[0]) > 0:
                    selected_hosts_per_leaf = np.delete(selected_hosts_per_leaf, indexes)
                    selected_hosts_count_per_leaf = np.delete(selected_hosts_count_per_leaf, indexes)
                    if len(selected_hosts_per_leaf) == 0:
                        available_leafs = np.delete(available_leafs, np.where(available_leafs == selected_leaf))
                    available_hosts_per_leaf[selected_leaf] = selected_hosts_per_leaf
                    available_hosts_count_per_leaf[selected_leaf] = selected_hosts_count_per_leaf

            vm_to_host_map[t] = vm_to_host
            vm_to_leaf_map[t] = vm_to_leaf

    def _colocate_random_random(self, is_sorted=False, is_reverse=False):
        # if is_sorted:
        #     vm_counts = sorted(self.tenants_maps['vm_counts'], reverse=is_reverse)
        # else:
        #     vm_counts = self.tenants_maps['vm_counts']

        vm_counts = self.tenants_maps['vm_counts']
        vm_to_host_map = self.placement_maps['vm_to_host']
        vm_to_leaf_map = self.placement_maps['vm_to_leaf']
        available_leafs = np.array(range(self.num_leafs), dtype=int)
        available_hosts_per_leaf = [None] * self.num_leafs
        available_hosts_count_per_leaf = [None] * self.num_leafs

        available_hosts_per_leaf[0] = np.array(range(self.num_hosts_per_leaf))
        available_hosts_count_per_leaf[0] = np.zeros(shape=self.num_hosts_per_leaf, dtype=int)
        for l in range(1, self.num_leafs):
            available_hosts_per_leaf[l] = available_hosts_per_leaf[l - 1] + self.num_hosts_per_leaf
            available_hosts_count_per_leaf[l] = np.zeros(shape=self.num_hosts_per_leaf, dtype=int)

        for t in range(self.num_tenants):
            vm_count = vm_counts[t]
            vm_to_host = np.empty(shape=vm_count, dtype=int)
            vm_to_leaf = np.empty(shape=vm_count, dtype=int)

            running_index = 0
            running_count = vm_count
            while running_count > 0:
                selected_leaf = np.random.choice(available_leafs, 1, replace=False)[0]
                selected_hosts_per_leaf = available_hosts_per_leaf[selected_leaf]
                selected_hosts_count_per_leaf = available_hosts_count_per_leaf[selected_leaf]
                selected_leaf_hosts_count = len(selected_hosts_per_leaf)

                # to ensure that we always pick hosts <= self.placement['num_hosts_per_leaf'] at each leaf
                if selected_leaf_hosts_count > self.num_hosts_per_leaf:
                    selected_leaf_hosts_count = self.num_hosts_per_leaf
                selected_hosts_per_leaf = np.random.choice(selected_hosts_per_leaf, selected_leaf_hosts_count,
                                                           replace=False)

                if int(running_count / selected_leaf_hosts_count) > 0:
                    vm_to_host[running_index:running_index + selected_leaf_hosts_count] = \
                        selected_hosts_per_leaf[0:selected_leaf_hosts_count]
                    vm_to_leaf[running_index:running_index + selected_leaf_hosts_count] = selected_leaf
                    for h in selected_hosts_per_leaf[0:selected_leaf_hosts_count]:
                        selected_hosts_count_per_leaf[np.where(selected_hosts_per_leaf == h)] += 1
                    running_index += selected_leaf_hosts_count
                    running_count -= selected_leaf_hosts_count
                else:
                    vm_to_host[running_index:running_index + running_count] = selected_hosts_per_leaf[0:running_count]
                    vm_to_leaf[running_index:running_index + running_count] = selected_leaf
                    for h in selected_hosts_per_leaf[0:running_count]:
                        selected_hosts_count_per_leaf[np.where(selected_hosts_per_leaf == h)] += 1
                    running_index += running_count
                    running_count = 0

                indexes = np.where(selected_hosts_count_per_leaf == self.max_vms_per_host)
                if len(indexes[0]) > 0:
                    selected_hosts_per_leaf = np.delete(selected_hosts_per_leaf, indexes)
                    selected_hosts_count_per_leaf = np.delete(selected_hosts_count_per_leaf, indexes)
                    if len(selected_hosts_per_leaf) == 0:
                        available_leafs = np.delete(available_leafs, np.where(available_leafs == selected_leaf))
                    available_hosts_per_leaf[selected_leaf] = selected_hosts_per_leaf
                    available_hosts_count_per_leaf[selected_leaf] = selected_hosts_count_per_leaf

            vm_to_host_map[t] = vm_to_host
            vm_to_leaf_map[t] = vm_to_leaf

    def _get_tenant_vms_to_host_map(self):
        if self.dist == 'uniform':
            self._uniform()
        elif self.dist == 'colocate-random-linear':
            self._colocate_random_linear()
        elif self.dist == 'colocate-random-random':
            self._colocate_random_random()
        elif self.dist == 'sorted-colocate-random-linear':
            self._colocate_random_linear(is_sorted=True)
        elif self.dist == 'sorted-colocate-random-random':
            self._colocate_random_random(is_sorted=True)
        elif self.dist == 'reverse-sorted-colocate-random-linear':
            self._colocate_random_linear(is_sorted=True, is_reverse=True)
        elif self.dist == 'reverse-sorted-colocate-random-random':
            self._colocate_random_random(is_sorted=True, is_reverse=True)
        else:
            raise (Exception("invalid dist parameter for vm allocation"))

    # def _get_tenant_groups_to_leafs_and_count_map(self):
    #     group_counts = self.tenants_maps['group_counts']
    #     t_groups = self.tenants_maps['groups']
    #     p_groups = self.placement_maps['groups']
    #     vm_to_leaf_map = self.placement_maps['vm_to_leaf']
    #     for t in bar_range(self.num_tenants, desc='placement:groups->leafs'):
    #         group_count = group_counts[t]
    #         vm_to_leaf = vm_to_leaf_map[t]
    #         t_group = t_groups[t]
    #         t_group_vms = t_group['vms']
    #         p_group = p_groups[t]
    #         p_group['leafs'] = [None] * group_count
    #         p_leafs = p_group['leafs']
    #         p_group['leaf_counts'] = np.empty(shape=group_count, dtype=int)
    #         p_leaf_counts = p_group['leaf_counts']
    #         for g in range(group_count):
    #             p_leafs[g] = np.unique(vm_to_leaf[t_group_vms[g]])
    #             p_leaf_counts[g] = len(p_leafs[g])

    # @staticmethod
    # def _get_tenant_groups_to_leafs_and_count_map(group_counts, t_groups, vm_to_leaf_map, num_tenants):
    #     groups_leafs = [None] * num_tenants
    #     groups_leaf_counts = [None] * num_tenants
    #     for t in range(num_tenants):
    #         group_count = group_counts[t]
    #         vm_to_leaf = vm_to_leaf_map[t]
    #         t_group = t_groups[t]
    #         t_group_vms = t_group['vms']
    #         groups_leafs[t] = [None] * group_count
    #         group_leafs = groups_leafs[t]
    #         groups_leaf_counts[t] = np.empty(shape=group_count, dtype=int)
    #         group_leaf_counts = groups_leaf_counts[t]
    #         for g in range(group_count):
    #             group_leafs[g] = np.unique(vm_to_leaf[t_group_vms[g]])
    #             group_leaf_counts[g] = len(group_leafs[g])
    #     return groups_leafs, groups_leaf_counts
    #
    # def _run_tenant_groups_to_leafs_and_count_map(self):
    #     if (self.num_tenants % self.num_jobs) != 0:
    #         raise (Exception('input not divisible by num_jobs'))
    #
    #     input_size = int(self.num_tenants / self.num_jobs)
    #     input_groups = [(i, i + input_size) for i in range(0, self.num_tenants, input_size)]
    #     inputs = [(self.tenants_maps['group_counts'][i:j],
    #                self.tenants_maps['groups'][i:j],
    #                self.placement_maps['vm_to_leaf'][i:j],
    #                input_size) for i, j in input_groups]
    #
    #     # pool = multiprocessing.Pool()
    #     # results = pool.map(unwrap_tenant_groups_to_leafs_and_count_map, [i for i in inputs])
    #
    #     num_cpus = multiprocessing.cpu_count()
    #     results = Parallel(n_jobs=num_cpus, backend="threading")(
    #         delayed(unwrap_tenant_groups_to_leafs_and_count_map)(i) for i in inputs)
    #
    #     p_groups = self.placement_maps['groups']
    #     for i in range(len(results)):
    #         result = results[i]
    #         t_low, t_high = input_groups[i]
    #         for j, t in enumerate(range(t_low, t_high)):
    #             p_group = p_groups[t]
    #             p_group['leafs'] = result[0][j]
    #             p_group['leaf_counts'] = result[1][j]

    # def _get_tenant_groups_leafs_to_hosts_and_bitmap_map(self):
    #     group_counts = self.tenants_maps['group_counts']
    #     t_groups = self.tenants_maps['groups']
    #     p_groups = self.placement_maps['groups']
    #     vm_to_host_map = self.placement_maps['vm_to_host']
    #     vm_to_leaf_map = self.placement_maps['vm_to_leaf']
    #     for t in bar_range(self.num_tenants, desc='placement:leafs->bitmap'):
    #         group_count = group_counts[t]
    #         vm_to_host = vm_to_host_map[t]
    #         vm_to_leaf = vm_to_leaf_map[t]
    #         t_group = t_groups[t]
    #         t_vms = t_group['vms']
    #         p_group = p_groups[t]
    #         p_maps = p_group['maps']
    #         p_maps['leafs'] = [None] * group_count
    #         p_leafs_map = p_maps['leafs']
    #         for g in range(group_count):
    #             p_leafs_map[g] = dict()
    #             p_leafs = p_leafs_map[g]
    #             for vm in t_vms[g]:
    #                 l = vm_to_leaf[vm]
    #                 h = vm_to_host[vm]
    #                 if l in p_leafs:
    #                     p_leafs[l]['hosts'] |= {h}
    #                 else:
    #                     p_leafs[l] = dict()
    #                     p_leafs[l]['hosts'] = {h}
    #             for l in p_leafs:
    #                 p_leafs[l]['bitmap'] = 0
    #                 for h in p_leafs[l]['hosts']:
    #                     p_leafs[l]['bitmap'] |= 1 << (h % self.num_hosts_per_leaf)

    @staticmethod
    def _get_tenant_groups_leafs_to_hosts_and_bitmap_map(group_counts, t_groups, vm_to_host_map,
                                                         vm_to_leaf_map, num_tenants, num_hosts_per_leaf):
        groups_leafs = [None] * num_tenants
        hosts, bitmap = 0, 1
        for t in bar_range(num_tenants, desc='placement:leafs->bitmaps'):
            group_count = group_counts[t]
            vm_to_host = vm_to_host_map[t]
            vm_to_leaf = vm_to_leaf_map[t]
            t_group = t_groups[t]
            t_vms = t_group['vms']
            groups_leafs[t] = [None] * group_count
            group_leafs = groups_leafs[t]
            for g in range(group_count):
                group_leafs[g] = dict()
                leafs = group_leafs[g]
                for vm in t_vms[g]:
                    l = vm_to_leaf[vm]
                    h = vm_to_host[vm]
                    if l in leafs:
                        leafs[l][hosts] += [h]
                    else:
                        leafs[l] = [None, None]
                        leafs[l][hosts] = [h]
                for l in leafs:
                    leafs[l][hosts] = np.unique(leafs[l][hosts])
                    leafs[l][bitmap] = 0
                    for h in leafs[l][hosts]:
                        leafs[l][bitmap] |= 1 << (h % num_hosts_per_leaf)
        return groups_leafs

    def _run_tenant_groups_leafs_to_hosts_and_bitmap_map(self):
        if (self.num_tenants % self.num_jobs) != 0:
            raise (Exception('input not divisible by num_jobs'))

        input_size = int(self.num_tenants / self.num_jobs)
        input_groups = [(i, i + input_size) for i in range(0, self.num_tenants, input_size)]
        inputs = [(self.tenants_maps['group_counts'][i:j],
                   self.tenants_maps['groups'][i:j],
                   self.placement_maps['vm_to_host'][i:j],
                   self.placement_maps['vm_to_leaf'][i:j],
                   input_size,
                   self.num_hosts_per_leaf) for i, j in input_groups]

        # pool = multiprocessing.Pool()
        # results = pool.map(unwrap_tenant_groups_leafs_to_hosts_and_bitmap_map, [i for i in inputs])

        num_cpus = multiprocessing.cpu_count()
        results = Parallel(n_jobs=num_cpus, backend="multiprocessing")(
            delayed(unwrap_tenant_groups_leafs_to_hosts_and_bitmap_map)(i) for i in inputs)

        p_groups = self.placement_maps['groups']
        for i in range(len(results)):
            result = results[i]
            t_low, t_high = input_groups[i]
            for j, t in enumerate(range(t_low, t_high)):
                p_groups[t]['maps']['leafs'] = result[j]
