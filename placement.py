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

    def _get_tenant_vm_to_host_map(self):
        self.tenant_vm_to_host_map = [None] * self.tenants.num_tenants

        if self.dist == 'uniform':
            for i in range(self.tenants.num_tenants):
                self.tenant_vm_to_host_map[i] = pd.Series(
                    np.random.choice(a=self.tenants.num_hosts,
                                     size=self.tenants.vm_map[i], replace=False))
            # TODO: take hosts out of sampling once exceed max_vms_count_per_host
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
