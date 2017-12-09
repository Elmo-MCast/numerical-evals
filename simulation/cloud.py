from simulation.placement import Placement
from simulation.tenants import Tenants


class Cloud:
    def __init__(self,
                 num_pods=11,
                 num_leafs_per_pod=48,
                 num_hosts_per_leaf=48,
                 max_vms_per_host=20,
                 num_tenants=3000,
                 min_vms_per_tenant=10,
                 max_vms_per_tenant=5000,
                 vm_dist='expon',  # options: expon, expon-mean, and geom
                 num_groups=100000,
                 min_group_size=5,
                 group_size_dist='uniform',  # options: uniform and wve
                 multi_threaded=True,
                 num_jobs=10):
        self.data = dict()

        Tenants(data=self.data,
                num_tenants=num_tenants, min_vms=min_vms_per_tenant, max_vms=max_vms_per_tenant, vm_dist=vm_dist,
                num_groups=num_groups, min_group_size=min_group_size, group_size_dist=group_size_dist, debug=False,
                multi_threaded=multi_threaded, num_jobs=num_jobs)

        Placement(data=self.data,
                  num_pods=num_pods, num_leafs_per_pod=num_leafs_per_pod, num_hosts_per_leaf=num_hosts_per_leaf,
                  num_tenants=num_tenants, max_vms_per_host=max_vms_per_host, multi_threaded=multi_threaded,
                  num_jobs=num_jobs)
