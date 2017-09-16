from simulation.network import Network
from simulation.optimization import Optimization
from simulation.placement import Placement
from simulation.tenants import Tenants


class Cloud:
    def __init__(self,
                 num_leafs=1056,
                 num_hosts_per_leaf=48,
                 num_rules_per_leaf=10000,
                 max_vms_per_host=20,
                 num_tenants=3000,
                 min_vms_per_tenant=10,
                 max_vms_per_tenant=5000,
                 vm_dist='expon',
                 num_groups=100000,
                 min_group_size=5,
                 group_size_dist='uniform',
                 placement_dist='uniform',
                 colocate_num_hosts_per_leaf=48,
                 num_bitmaps=32):
        self.data = dict()

        Network(data=self.data, num_leafs=num_leafs, num_hosts_per_leaf=num_hosts_per_leaf,
                num_rules_per_leaf=num_rules_per_leaf)

        Tenants(data=self.data,
                max_vms_per_host=max_vms_per_host,
                num_tenants=num_tenants,
                min_vms=min_vms_per_tenant, max_vms=max_vms_per_tenant, vm_dist=vm_dist,
                num_groups=num_groups, min_group_size=min_group_size,
                group_size_dist=group_size_dist)

        Placement(data=self.data, dist=placement_dist, num_bitmaps=num_bitmaps,
                  num_hosts_per_leaf=colocate_num_hosts_per_leaf)

        Optimization(data=self.data)
