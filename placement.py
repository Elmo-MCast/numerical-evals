import pandas as pd
import numpy as np
import copy


class Placement:
    def __init__(self, network, tenants, dist='uniform'):
        self.dist = dist
        self.network = network
        self.tenants = tenants

        self.tenant_vm_to_host_map = None
        self._get_tenant_vm_to_host_map()

        self.tenant_vm_to_leaf_map = None
        self._get_tenant_vm_to_leaf_map()

        self.tenant_group_to_leaf_map = None
        self._get_tenant_group_to_leaf_map()

        self.tenant_group_to_leaf_count = None
        self._get_tenant_group_to_leaf_count()

    # def _get_tenant_vm_to_host_map(self):
    #     self.tenant_vm_to_host_map = [None] * self.tenants.num_tenants
    #
    #     if self.dist == 'uniform':
    #         for i in range(self.tenants.num_tenants):
    #             self.tenant_vm_to_host_map[i] = pd.Series(
    #                 np.random.choice(a=self.tenants.num_hosts,
    #                                  size=self.tenants.vm_map[i], replace=False))
    #     else:
    #         raise (Exception("invalid dist parameter for vm to host allocation"))

    def _get_tenant_vm_to_host_map(self):
        if self.dist == 'uniform':
            self.tenant_vm_to_host_map = [None] * self.tenants.num_tenants
            available_hosts = [i for i in range(self.tenants.num_hosts)]
            selected_hosts_counts = [0] * self.tenants.num_hosts

            for i in range(self.tenants.num_tenants):
                self.tenant_vm_to_host_map[i] = pd.Series(
                    np.random.choice(a=available_hosts,
                                     size=self.tenants.vm_map[i], replace=False))

                for _, value in self.tenant_vm_to_host_map[i].iteritems():
                    selected_hosts_counts[value] += 1

                max_host_count = max(selected_hosts_counts)
                if max_host_count == self.tenants.max_vms_per_host:
                    removed_hosts = [j for j, host_count in enumerate(selected_hosts_counts)
                                     if host_count == max_host_count]
                    available_hosts = list(set(available_hosts) - set(removed_hosts))
                    for removed_host in sorted(removed_hosts, reverse=True):
                        selected_hosts_counts[removed_host] = -1
        elif self.dist == 'colocate':
            self.tenant_vm_to_host_map = [None] * self.tenants.num_tenants
            available_leafs = [i for i in range(self.network.num_leafs)]

            available_hosts_per_leaf = [None] * self.network.num_leafs
            selected_hosts_counts_per_leaf = [None] * self.network.num_leafs
            for i in range(self.network.num_leafs):
                available_hosts_per_leaf[i] = [(i * self.network.num_hosts_per_leaf) + j
                                               for j in range(self.network.num_hosts_per_leaf)]
                selected_hosts_counts_per_leaf[i] = [0] * self.network.num_hosts_per_leaf

            for i in range(self.tenants.num_tenants):
                self.tenant_vm_to_host_map[i] = pd.Series([None] * self.tenants.vm_map[i])

                running_index = 0
                running_count = self.tenants.vm_map[i]
                while running_count > 0:
                    selected_leaf = np.random.choice(a=available_leafs, size=1)[0]
                    selected_leaf_hosts_count = len(available_hosts_per_leaf[selected_leaf])

                    if int(running_count/selected_leaf_hosts_count) > 0:
                        for j in range(selected_leaf_hosts_count):
                            self.tenant_vm_to_host_map[i][running_index] = available_hosts_per_leaf[selected_leaf][j]
                            selected_hosts_counts_per_leaf[selected_leaf][j] += 1
                            running_index += 1
                        running_count -= selected_leaf_hosts_count
                    else:
                        for j in range(running_count):
                            self.tenant_vm_to_host_map[i][running_index] = available_hosts_per_leaf[selected_leaf][j]
                            selected_hosts_counts_per_leaf[selected_leaf][j] += 1
                            running_index += 1
                        running_count = 0

                    max_host_count = max(selected_hosts_counts_per_leaf[selected_leaf])
                    if max_host_count == self.tenants.max_vms_per_host:
                        removed_hosts = [j for j, host_count in enumerate(selected_hosts_counts_per_leaf[selected_leaf])
                                         if host_count == max_host_count]
                        for removed_host in sorted(removed_hosts, reverse=True):
                            del available_hosts_per_leaf[selected_leaf][removed_host]
                            del selected_hosts_counts_per_leaf[selected_leaf][removed_host]

                        if len(available_hosts_per_leaf[selected_leaf]) == 0:
                            available_leafs.remove(selected_leaf)
        else:
            raise (Exception("invalid dist parameter for vm to host allocation"))

    def _get_tenant_vm_to_leaf_map(self):
        self.tenant_vm_to_leaf_map = [None] * self.tenants.num_tenants

        for i in range(self.tenants.num_tenants):
            self.tenant_vm_to_leaf_map[i] = pd.Series([self.network.host_to_leaf_map[value]
                                                       for _, value in self.tenant_vm_to_host_map[i].iteritems()])

    def _get_tenant_group_to_leaf_map(self):
        self.tenant_group_to_leaf_map = [None] * self.tenants.num_tenants

        for i in range(self.tenants.num_tenants):
            _tenant_group_to_leaf_map = [None] * self.tenants.group_map[i]

            for j in range(self.tenants.group_map[i]):
                _tenant_group_to_leaf_map[j] = pd.Series([self.tenant_vm_to_leaf_map[i][value]
                                                         for _, value in self.tenants.group_to_vm_map[i][j].iteritems()])
            self.tenant_group_to_leaf_map[i] = _tenant_group_to_leaf_map

    def _get_tenant_group_to_leaf_count(self):
        self.tenant_group_to_leaf_count = [None] * self.tenants.num_tenants

        for i in range(self.tenants.num_tenants):
            _tenant_group_to_leaf_count = [None] * self.tenants.group_map[i]

            for j in range(self.tenants.group_map[i]):
                _tenant_group_to_leaf_count[j] = len(self.tenant_group_to_leaf_map[i][j].unique())

            self.tenant_group_to_leaf_count[i] = pd.Series(_tenant_group_to_leaf_count)
