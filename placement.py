import pandas as pd
import numpy as np


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
        self.tenant_vm_to_host_map = [None] * self.tenants.num_tenants
        available_hosts = [i for i in range(self.tenants.num_hosts)]
        selected_host_counts = [0] * self.tenants.num_hosts

        if self.dist == 'uniform':
            for i in range(self.tenants.num_tenants):
                self.tenant_vm_to_host_map[i] = pd.Series(
                    np.random.choice(a=available_hosts,
                                     size=self.tenants.vm_map[i], replace=False))

                for _, value in self.tenant_vm_to_host_map[i].iteritems():
                    selected_host_counts[value] += 1

                max_host_count = max(selected_host_counts)
                if max_host_count == self.tenants.max_vms_per_host:
                    removed_hosts = [j for j, host_count in enumerate(selected_host_counts)
                                     if host_count == max_host_count]
                    available_hosts = list(set(available_hosts) - set(removed_hosts))
                    for removed_host in removed_hosts:
                        selected_host_counts[removed_host] = -1
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
