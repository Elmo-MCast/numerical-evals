import random
import numpy as np
from simulation.utils import bar_range


class Placement:
    def __init__(self, data, dist='uniform',  # options: uniform, colocate-random-linear, colocate-random-random
                 num_bitmaps=32, num_hosts_per_leaf=48):
        self.data = data
        self.dist = dist
        self.num_bitmaps = num_bitmaps

        self.network = self.data['network']
        self.network_maps = self.network['maps']
        self.tenants = self.data['tenants']
        self.tenants_maps = self.tenants['maps']

        self.data['placement'] = {'dist': dist,
                                  'num_bitmaps': num_bitmaps,
                                  'num_hosts_per_leaf': num_hosts_per_leaf}
        self.placement = self.data['placement']

        for t in range(self.tenants['num_tenants']):
            self.tenants_maps[t]['vms_map'] = \
                [{'host': None, 'leaf': None} for _ in range(self.tenants_maps[t]['vm_count'])]
            for g in range(self.tenants_maps[t]['group_count']):
                self.tenants_maps[t]['groups_map'][g]['leaf_count'] = None
                self.tenants_maps[t]['groups_map'][g]['leafs'] = None
                self.tenants_maps[t]['groups_map'][g]['leafs_map'] = dict()

        self._get_tenant_vms_to_host_map()

        self._get_tenant_vms_to_leaf_map()

        self._get_tenant_groups_to_leafs_and_count_map()

        self._get_tenant_groups_leafs_to_hosts_and_bitmap_map()

    def _uniform(self):
        available_hosts = [h for h in range(self.tenants['num_hosts'])]
        available_hosts_count = [0] * self.tenants['num_hosts']

        for t in bar_range(self.tenants['num_tenants'], desc='placement:vms->host'):
            hosts = random.sample(available_hosts, self.tenants_maps[t]['vm_count'])

            for v, host in enumerate(hosts):
                self.tenants_maps[t]['vms_map'][v]['host'] = host
                available_hosts_count[host] += 1

            max_host_count = max(available_hosts_count)
            if max_host_count == self.tenants['max_vms_per_host']:
                removed_hosts = [h for h, host_count in enumerate(available_hosts_count)
                                 if host_count == max_host_count]
                available_hosts = list(set(available_hosts) - set(removed_hosts))
                for removed_host in sorted(removed_hosts, reverse=True):
                    available_hosts_count[removed_host] = -1

    def _colocate_random_linear(self, is_sorted=False, is_reverse=False):
        available_leafs = [l for l in range(self.network['num_leafs'])]
        available_hosts_per_leaf = [None] * self.network['num_leafs']
        available_hosts_count_per_leaf = [None] * self.network['num_leafs']

        for l in range(self.network['num_leafs']):
            available_hosts_per_leaf[l] = [(l * self.network['num_hosts_per_leaf']) + h
                                           for h in range(self.network['num_hosts_per_leaf'])]
            available_hosts_count_per_leaf[l] = [0] * self.network['num_hosts_per_leaf']

        if is_sorted:
            tenants_maps = sorted(self.tenants_maps, key=lambda item: item['vm_count'], reverse=is_reverse)
        else:
            tenants_maps = self.tenants_maps
        for t in bar_range(self.tenants['num_tenants'], desc='placement:vms->host'):
            running_index = 0
            running_count = tenants_maps[t]['vm_count']
            while running_count > 0:
                selected_leaf = random.sample(available_leafs, 1)[0]
                selected_leaf_hosts_count = len(available_hosts_per_leaf[selected_leaf])

                # to ensure that we always pick hosts <= self.placement['num_hosts_per_leaf'] at each leaf
                if selected_leaf_hosts_count > self.placement['num_hosts_per_leaf']:
                    selected_leaf_hosts_count = self.placement['num_hosts_per_leaf']

                if int(running_count / selected_leaf_hosts_count) > 0:
                    for h in range(selected_leaf_hosts_count):
                        tenants_maps[t]['vms_map'][running_index]['host'] = \
                            available_hosts_per_leaf[selected_leaf][h]
                        available_hosts_count_per_leaf[selected_leaf][h] += 1
                        running_index += 1
                    running_count -= selected_leaf_hosts_count
                else:
                    for h in range(running_count):
                        tenants_maps[t]['vms_map'][running_index]['host'] = \
                            available_hosts_per_leaf[selected_leaf][h]
                        available_hosts_count_per_leaf[selected_leaf][h] += 1
                        running_index += 1
                    running_count = 0

                max_host_count = max(available_hosts_count_per_leaf[selected_leaf])
                if max_host_count == self.tenants['max_vms_per_host']:
                    removed_hosts = [h for h, host_count in enumerate(available_hosts_count_per_leaf[selected_leaf])
                                     if host_count == max_host_count]
                    for removed_host in sorted(removed_hosts, reverse=True):
                        del available_hosts_per_leaf[selected_leaf][removed_host]
                        del available_hosts_count_per_leaf[selected_leaf][removed_host]

                    if len(available_hosts_per_leaf[selected_leaf]) == 0:
                        available_leafs.remove(selected_leaf)

    def _colocate_random_random(self, is_sorted=False, is_reverse=False):
        available_leafs = [l for l in range(self.network['num_leafs'])]
        available_hosts_per_leaf = [None] * self.network['num_leafs']
        available_hosts_count_per_leaf = [None] * self.network['num_leafs']

        for l in range(self.network['num_leafs']):
            available_hosts_per_leaf[l] = [(l * self.network['num_hosts_per_leaf']) + h
                                           for h in range(self.network['num_hosts_per_leaf'])]
            available_hosts_count_per_leaf[l] = [0] * self.network['num_hosts_per_leaf']

        if is_sorted:
            tenants_maps = sorted(self.tenants_maps, key=lambda item: item['vm_count'], reverse=is_reverse)
        else:
            tenants_maps = self.tenants_maps
        for t in bar_range(self.tenants['num_tenants'], desc='placement:vms->host'):
            running_index = 0
            running_count = tenants_maps[t]['vm_count']
            while running_count > 0:
                selected_leaf = random.sample(available_leafs, 1)[0]
                selected_leaf_hosts = available_hosts_per_leaf[selected_leaf]
                selected_leaf_hosts_count = len(available_hosts_per_leaf[selected_leaf])

                # to ensure that we always pick hosts <= self.placement['num_hosts_per_leaf'] at each leaf
                if selected_leaf_hosts_count > self.placement['num_hosts_per_leaf']:
                    selected_leaf_hosts = random.sample(selected_leaf_hosts, self.placement['num_hosts_per_leaf'])
                    selected_leaf_hosts_count = self.placement['num_hosts_per_leaf']

                if int(running_count / selected_leaf_hosts_count) > 0:
                    for h in range(selected_leaf_hosts_count):
                        tenants_maps[t]['vms_map'][running_index]['host'] = \
                            selected_leaf_hosts[h]
                        available_hosts_count_per_leaf[selected_leaf][
                            available_hosts_per_leaf[selected_leaf].index(selected_leaf_hosts[h])] += 1
                        running_index += 1
                    running_count -= selected_leaf_hosts_count
                else:
                    for h in range(running_count):
                        tenants_maps[t]['vms_map'][running_index]['host'] = \
                            selected_leaf_hosts[h]
                        available_hosts_count_per_leaf[selected_leaf][
                            available_hosts_per_leaf[selected_leaf].index(selected_leaf_hosts[h])] += 1
                        running_index += 1
                    running_count = 0

                max_host_count = max(available_hosts_count_per_leaf[selected_leaf])
                if max_host_count == self.tenants['max_vms_per_host']:
                    removed_hosts = [h for h, host_count in enumerate(available_hosts_count_per_leaf[selected_leaf])
                                     if host_count == max_host_count]
                    for removed_host in sorted(removed_hosts, reverse=True):
                        del available_hosts_per_leaf[selected_leaf][removed_host]
                        del available_hosts_count_per_leaf[selected_leaf][removed_host]

                    if len(available_hosts_per_leaf[selected_leaf]) == 0:
                        available_leafs.remove(selected_leaf)

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
            raise (Exception("invalid dist parameter for vm to host allocation"))

    def _get_tenant_vms_to_leaf_map(self):
        for t in bar_range(self.tenants['num_tenants'], desc='placement:vms->leaf'):
            for v in range(self.tenants_maps[t]['vm_count']):
                self.tenants_maps[t]['vms_map'][v]['leaf'] = \
                    self.network_maps['host_to_leaf'][self.tenants_maps[t]['vms_map'][v]['host']]

    def _get_tenant_groups_to_leafs_and_count_map(self):
        for t in bar_range(self.tenants['num_tenants'], desc='placement:groups->leafs'):
            for g in range(self.tenants_maps[t]['group_count']):
                self.tenants_maps[t]['groups_map'][g]['leafs'] = list(
                    {self.tenants_maps[t]['vms_map'][vm]['leaf']
                     for vm in self.tenants_maps[t]['groups_map'][g]['vms']})
                self.tenants_maps[t]['groups_map'][g]['leaf_count'] = \
                    len(self.tenants_maps[t]['groups_map'][g]['leafs'])

    def _get_tenant_groups_leafs_to_hosts_and_bitmap_map(self):
        for t in bar_range(self.tenants['num_tenants'], desc='placement:leafs->bitmap'):
            for g in range(self.tenants_maps[t]['group_count']):
                for vm in self.tenants_maps[t]['groups_map'][g]['vms']:
                    if self.tenants_maps[t]['vms_map'][vm]['leaf'] in \
                            self.tenants_maps[t]['groups_map'][g]['leafs_map']:
                        self.tenants_maps[t]['groups_map'][g]['leafs_map'][
                            self.tenants_maps[t]['vms_map'][vm]['leaf']]['hosts'] |= {
                            self.tenants_maps[t]['vms_map'][vm]['host']}
                    else:
                        self.tenants_maps[t]['groups_map'][g]['leafs_map'][
                            self.tenants_maps[t]['vms_map'][vm]['leaf']] = dict()
                        self.tenants_maps[t]['groups_map'][g]['leafs_map'][
                            self.tenants_maps[t]['vms_map'][vm]['leaf']]['hosts'] = {
                            self.tenants_maps[t]['vms_map'][vm]['host']}

                for l in self.tenants_maps[t]['groups_map'][g]['leafs_map']:
                    self.tenants_maps[t]['groups_map'][g]['leafs_map'][l]['bitmap'] = np.array(
                        [0] * self.network['num_hosts_per_leaf'])

                    for h in self.tenants_maps[t]['groups_map'][g]['leafs_map'][l]['hosts']:
                        self.tenants_maps[t]['groups_map'][g]['leafs_map'][l]['bitmap'][
                            h % self.network['num_hosts_per_leaf']] = 1
