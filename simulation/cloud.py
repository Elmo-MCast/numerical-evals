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
        num_tenants = self.num_tenants
        tenants = self.data['tenants']
        tenants_maps = tenants['maps']

        data = dict()
        data['tenants'] = dict()
        data_tenants = data['tenants']
        data_tenants['vm_count'] = tenants['vm_count']
        data_tenants['group_count'] = tenants['group_count']
        data_tenants['maps'] = [{'vm_count': None,
                                 'group_count': None,
                                 'groups_map': None} for _ in range(num_tenants)]
        data_tenants_maps = data_tenants['maps']
        for t in bar_range(num_tenants, desc='pruning'):
            tenant_maps = tenants_maps[t]
            groups_map = tenant_maps['groups_map']

            data_tenant_map = data_tenants_maps[t]
            data_tenant_map['vm_count'] = tenant_maps['vm_count']
            data_tenant_map['group_count'] = tenant_maps['group_count']
            data_group_count = data_tenant_map['group_count']
            data_tenant_map['groups_map'] = [{'size': None,
                                              'leaf_count': None,
                                              'leafs_map': None} for _ in range(data_group_count)]
            data_groups_map = data_tenant_map['groups_map']
            for g in range(data_group_count):
                group_map = groups_map[g]
                leafs_map = group_map['leafs_map']

                data_group_map = data_groups_map[g]
                data_group_map['size'] = group_map['size']
                data_group_map['leaf_count'] = group_map['leaf_count']
                data_group_map['leafs_map'] = dict()
                data_leafs_map = data_group_map['leafs_map']
                for l in leafs_map:
                    data_leafs_map[l] = dict()
                    data_leafs_map[l]['bitmap'] = leafs_map[l]['bitmap']

        return data
