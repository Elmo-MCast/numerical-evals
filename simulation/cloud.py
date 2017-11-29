from simulation.network import Network
from simulation.placement import Placement
from simulation.tenants import Tenants
from simulation.utils import bar_range


class Cloud:
    def __init__(self,
                 num_leafs=1056,
                 num_hosts_per_leaf=48,
                 max_vms_per_host=20,
                 num_tenants=3000,
                 min_vms_per_tenant=10,
                 max_vms_per_tenant=5000,
                 vm_dist='expon',  # options: expon, expon-mean, and geom
                 num_groups=100000,
                 min_group_size=5,
                 group_size_dist='uniform',  # options: uniform and wve
                 placement_dist='uniform',  # options: uniform, colocate-random-linear, and colocate-random-random
                 colocate_num_hosts_per_leaf=48,
                 multi_threaded=True,
                 num_jobs=10):
        self.data = dict()
        self.num_tenants = num_tenants

        Network(data=self.data,
                num_leafs=num_leafs, num_hosts_per_leaf=num_hosts_per_leaf)

        Tenants(data=self.data,
                num_leafs=num_leafs, num_hosts_per_leaf=num_hosts_per_leaf,
                max_vms_per_host=max_vms_per_host, num_tenants=num_tenants,
                min_vms=min_vms_per_tenant, max_vms=max_vms_per_tenant, vm_dist=vm_dist,
                num_groups=num_groups, min_group_size=min_group_size, group_size_dist=group_size_dist,
                debug=False, multi_threaded=multi_threaded, num_jobs=num_jobs)

        Placement(data=self.data,
                  num_leafs=num_leafs, num_hosts_per_leaf=num_hosts_per_leaf,
                  num_tenants=num_tenants, max_vms_per_host=max_vms_per_host,
                  dist=placement_dist, colocate_num_hosts_per_leaf=colocate_num_hosts_per_leaf,
                  multi_threaded=multi_threaded, num_jobs=num_jobs)

    def prune(self):
        del self.data['network']

        num_tenants = self.num_tenants
        tenants = self.data['tenants']
        tenants_maps = tenants['maps']
        for t in bar_range(num_tenants, desc='pruning'):
            tenant_maps = tenants_maps[t]
            del tenant_maps['vms_map']

            group_count = tenant_maps['group_count']
            groups_map = tenant_maps['groups_map']
            for g in range(group_count):
                group_map = groups_map[g]
                del group_map['vms']
                del group_map['leafs']

                leafs_map = group_map['leafs_map']
                for l in leafs_map:
                    leaf_map = leafs_map[l]
                    del leaf_map['hosts']
