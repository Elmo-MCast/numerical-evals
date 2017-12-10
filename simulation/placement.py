import random
import multiprocessing
from joblib import Parallel, delayed
from simulation.utils import bar_range


def unwrap_tenant_groups_pods_and_leafs_to_bitmap_map(args, **kwargs):
    return Placement._get_tenant_groups_pods_and_leafs_to_bitmap_map_mproc(*args, **kwargs)


class Placement:
    def __init__(self, data, num_pods=12, num_leafs_per_pod=48, num_hosts_per_leaf=48, num_tenants=3000,
                 max_vms_per_host=20, dist='colocate-uniform', allocate_num_hosts_per_leaf=48, multi_threaded=False,
                 num_jobs=4):
        self.data = data
        self.num_pods = num_pods
        self.num_leafs_per_pod = num_leafs_per_pod
        self.num_hosts_per_leaf = num_hosts_per_leaf
        self.num_tenants = num_tenants
        self.max_vms_per_host = max_vms_per_host
        self.dist = dist
        self.allocate_num_hosts_per_leaf = allocate_num_hosts_per_leaf
        self.multi_threaded = multi_threaded
        self.num_jobs = num_jobs

        self.tenants = self.data['tenants']
        self.tenants_maps = self.tenants['maps']

        for t in range(self.num_tenants):
            tenant_maps = self.tenants_maps[t]
            tenant_maps['vm_to_host_map'] = [None for _ in range(tenant_maps['vm_count'])]

            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']
            for g in range(group_count):
                group_map = groups_map[g]
                group_map['leafs_map'] = dict()
                group_map['pods_map'] = dict()

        self._get_tenant_vms_to_host_map()
        if not self.multi_threaded:
            self._get_tenant_groups_pods_and_leafs_to_bitmap_map()
        else:
            self._run_tenant_groups_pods_and_leafs_to_bitmap_map()

    def _colocate_pods__uniform_hosts(self):
        available_pods = list(range(self.num_pods))
        available_hosts_per_pod = [None] * self.num_pods
        available_hosts_count_per_pod = [None] * self.num_pods

        for p in range(self.num_pods):
            available_hosts_per_pod[p] = [(((p * self.num_leafs_per_pod) + l) * self.num_hosts_per_leaf) + h
                                          for l in range(self.num_leafs_per_pod)
                                          for h in range(self.num_hosts_per_leaf)]
            available_hosts_count_per_pod[p] = [0] * self.num_leafs_per_pod * self.num_hosts_per_leaf

        tenants_maps = self.tenants_maps
        for t in bar_range(self.num_tenants, desc='placement:vms->host'):
            tenant_maps = tenants_maps[t]
            vm_to_host_map = tenant_maps['vm_to_host_map']
            vm_index = 0
            vm_count = tenant_maps['vm_count']

            while vm_count > 0:
                selected_pod = random.sample(available_pods, 1)[0]
                selected_pod_index = available_pods.index(selected_pod)
                selected_hosts = available_hosts_per_pod[selected_pod_index]
                selected_hosts_count = available_hosts_count_per_pod[selected_pod_index]

                sampled_hosts = random.sample(selected_hosts, min(len(selected_hosts), vm_count))
                for h in sampled_hosts:
                    vm_to_host_map[vm_index] = h
                    selected_hosts_count[selected_hosts.index(h)] += 1
                    vm_index += 1
                vm_count -= len(sampled_hosts)

                removed_hosts_indexes = [i for i, c in enumerate(selected_hosts_count) if c == self.max_vms_per_host]
                for i in sorted(removed_hosts_indexes, reverse=True):
                    del selected_hosts[i]
                    del selected_hosts_count[i]

                if len(selected_hosts) == 0:
                    del available_pods[selected_pod_index]
                    del available_hosts_per_pod[selected_pod_index]
                    del available_hosts_count_per_pod[selected_pod_index]

    def _colocate_pods__colocate_leafs__uniform_hosts(self):
        available_pods = list(range(self.num_pods))
        available_leafs_per_pod = [None] * self.num_pods
        available_hosts_per_leaf_per_pod = [None] * self.num_pods
        available_hosts_count_per_leaf_per_pod = [None] * self.num_pods

        for p in range(self.num_pods):
            available_leafs_per_pod[p] = [(p * self.num_leafs_per_pod) + l for l in range(self.num_leafs_per_pod)]
            available_hosts_per_leaf_per_pod[p] = [None] * self.num_leafs_per_pod
            available_hosts_count_per_leaf_per_pod[p] = [None] * self.num_leafs_per_pod

            available_leafs = available_leafs_per_pod[p]
            available_hosts_per_leaf = available_hosts_per_leaf_per_pod[p]
            available_hosts_count_per_leaf = available_hosts_count_per_leaf_per_pod[p]
            for l in range(self.num_leafs_per_pod):
                available_hosts_per_leaf[l] = [(available_leafs[l] * self.num_hosts_per_leaf) + h
                                               for h in range(self.num_hosts_per_leaf)]
                available_hosts_count_per_leaf[l] = [0] * self.num_hosts_per_leaf

        tenants_maps = self.tenants_maps
        for t in bar_range(self.num_tenants, desc='placement:vms->host'):
            tenant_maps = tenants_maps[t]
            vm_to_host_map = tenant_maps['vm_to_host_map']
            vm_index = 0
            vm_count = tenant_maps['vm_count']

            while vm_count > 0:
                selected_pod = random.sample(available_pods, 1)[0]
                selected_pod_index = available_pods.index(selected_pod)
                selected_leafs = available_leafs_per_pod[selected_pod_index]
                selected_hosts_per_leaf = available_hosts_per_leaf_per_pod[selected_pod_index]
                selected_hosts_count_per_leaf = available_hosts_count_per_leaf_per_pod[selected_pod_index]

                while vm_count > 0 and len(selected_leafs) > 0:
                    selected_leaf = random.sample(selected_leafs, 1)[0]
                    selected_leaf_index = selected_leafs.index(selected_leaf)
                    selected_hosts = selected_hosts_per_leaf[selected_leaf_index]
                    selected_hosts_count = selected_hosts_count_per_leaf[selected_leaf_index]

                    sampled_hosts = random.sample(selected_hosts, min(len(selected_hosts), vm_count))
                    for h in sampled_hosts:
                        vm_to_host_map[vm_index] = h
                        selected_hosts_count[selected_hosts.index(h)] += 1
                        vm_index += 1
                    vm_count -= len(sampled_hosts)

                    removed_hosts_indexes = [i for i, c in enumerate(selected_hosts_count) if c == self.max_vms_per_host]
                    for i in sorted(removed_hosts_indexes, reverse=True):
                        del selected_hosts[i]
                        del selected_hosts_count[i]

                    if len(selected_hosts) == 0:
                        del selected_leafs[selected_leaf_index]
                        del selected_hosts_per_leaf[selected_leaf_index]
                        del selected_hosts_count_per_leaf[selected_leaf_index]

                if len(selected_leafs) == 0:
                    del available_pods[selected_pod_index]
                    del available_leafs_per_pod[selected_pod_index]
                    del available_hosts_per_leaf_per_pod[selected_pod_index]
                    del available_hosts_count_per_leaf_per_pod[selected_pod_index]

    def _get_tenant_vms_to_host_map(self):
        if self.dist == 'colocate-uniform':
            self._colocate_pods__uniform_hosts()
        elif self.dist == 'colocate-colocate-uniform':
            self._colocate_pods__colocate_leafs__uniform_hosts()
        else:
            raise(Exception('invalid dist parameter for vm to host allocation'))

    def _get_tenant_groups_pods_and_leafs_to_bitmap_map(self):
        for t in bar_range(self.num_tenants, desc='placement:leafs->bitmap'):
            tenant_maps = self.tenants_maps[t]
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']
            vm_to_host_map = tenant_maps['vm_to_host_map']

            for g in range(group_count):
                group_map = groups_map[g]
                vms = group_map['vms']
                leafs_map = group_map['leafs_map']
                pods_map = group_map['pods_map']
                for vm in vms:
                    host = vm_to_host_map[vm]
                    leaf = int(host / self.num_hosts_per_leaf)
                    pod = int(leaf / self.num_leafs_per_pod)

                    if leaf in leafs_map:
                        leafs_map[leaf]['hosts'] |= {host}
                    else:
                        leafs_map[leaf] = dict()
                        leafs_map[leaf]['hosts'] = {host}

                    if pod in pods_map:
                        pods_map[pod]['leafs'] |= {leaf}
                    else:
                        pods_map[pod] = dict()
                        pods_map[pod]['leafs'] = {leaf}

                for l in leafs_map:
                    leaf_map = leafs_map[l]
                    leaf_map['bitmap'] = 0
                    for h in leaf_map['hosts']:
                        leaf_map['bitmap'] |= 1 << (h % self.num_hosts_per_leaf)
                    del leaf_map['hosts']

                for p in pods_map:
                    pod_map = pods_map[p]
                    pod_map['bitmap'] = 0
                    for l in pod_map['leafs']:
                        pod_map['bitmap'] |= 1 << (l % self.num_leafs_per_pod)
                    del pod_map['leafs']

    @staticmethod
    def _get_tenant_groups_pods_and_leafs_to_bitmap_map_mproc(tenants_maps, num_tenants, num_hosts_per_leaf,
                                                              num_leafs_per_pod):
        for t in bar_range(num_tenants, desc='placement:leafs->bitmap'):
            tenant_maps = tenants_maps[t]
            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']
            vm_to_host_map = tenant_maps['vm_to_host_map']

            for g in range(group_count):
                group_map = groups_map[g]
                vms = group_map['vms']
                leafs_map = group_map['leafs_map']
                pods_map = group_map['pods_map']
                for vm in vms:
                    host = vm_to_host_map[vm]
                    leaf = int(host / num_hosts_per_leaf)
                    pod = int(leaf / num_leafs_per_pod)

                    if leaf in leafs_map:
                        leafs_map[leaf]['hosts'] |= {host}
                    else:
                        leafs_map[leaf] = dict()
                        leafs_map[leaf]['hosts'] = {host}

                    if pod in pods_map:
                        pods_map[pod]['leafs'] |= {leaf}
                    else:
                        pods_map[pod] = dict()
                        pods_map[pod]['leafs'] = {leaf}

                for l in leafs_map:
                    leaf_map = leafs_map[l]
                    leaf_map['bitmap'] = 0
                    for h in leaf_map['hosts']:
                        leaf_map['bitmap'] |= 1 << (h % num_hosts_per_leaf)
                    del leaf_map['hosts']

                for p in pods_map:
                    pod_map = pods_map[p]
                    pod_map['bitmap'] = 0
                    for l in pod_map['leafs']:
                        pod_map['bitmap'] |= 1 << (l % num_leafs_per_pod)
                    del pod_map['leafs']

        return tenants_maps

    def _run_tenant_groups_pods_and_leafs_to_bitmap_map(self):
        if (self.num_tenants % self.num_jobs) != 0:
            raise (Exception('input not divisible by num_jobs'))

        input_size = int(self.num_tenants / self.num_jobs)
        input_groups = [(i, i + input_size) for i in range(0, self.num_tenants, input_size)]
        inputs = [(self.tenants_maps[i:j],
                   input_size,
                   self.num_hosts_per_leaf,
                   self.num_leafs_per_pod) for i, j in input_groups]

        # pool = multiprocessing.Pool()
        # results = pool.map(unwrap_tenant_groups_leafs_to_hosts_and_bitmap_map, [i for i in inputs])

        num_cpus = multiprocessing.cpu_count()
        Parallel(n_jobs=num_cpus, backend="threading")(
            delayed(unwrap_tenant_groups_pods_and_leafs_to_bitmap_map)(i) for i in inputs)
