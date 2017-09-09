from network import *
from tenants import *
from placement import *
from optimization import *


class Cloud:
    def __init__(self,
                 num_leafs=1056,
                 num_hosts_per_leaf=48,
                 max_vms_per_host=20,
                 num_tenants=3000,
                 min_vms_per_tenant=10,
                 max_vms_per_tenant=5000,
                 vm_dist='expon',
                 num_groups=100000,
                 min_group_size=5,
                 group_size_dist='uniform',
                 placement_dist='uniform',
                 num_bitmaps=32,
                 generate_bitmaps=False,
                 multi_threaded=True,
                 num_threads=4):
        self.network = Network(num_leafs=num_leafs, num_hosts_per_leaf=num_hosts_per_leaf,
                               multi_threaded=multi_threaded, num_threads=num_threads)

        self.tenants = Tenants(num_hosts=self.network.num_hosts,
                               max_vms_per_host=max_vms_per_host,
                               num_tenants=num_tenants,
                               min_vms=min_vms_per_tenant, max_vms=max_vms_per_tenant, vm_dist=vm_dist,
                               num_groups=num_groups, min_group_size=min_group_size,
                               group_size_dist=group_size_dist,
                               multi_threaded=multi_threaded, num_threads=num_threads)

        self.placement = Placement(network=self.network, tenants=self.tenants, dist=placement_dist,
                                   num_bitmaps=num_bitmaps, generate_bitmaps=generate_bitmaps)

        self.optimization = Optimization(network=self.network, tenants=self.tenants, placement=self.placement)
