import alternate.network as network
import alternate.tenants as tenants
import alternate.placement as placement
import alternate.optimization as optimization


def initialize(num_leafs=1056,
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
    _network = network.initialize(num_leafs=num_leafs, num_hosts_per_leaf=num_hosts_per_leaf,
                                  multi_threaded=multi_threaded, num_threads=num_threads)

    _tenants = tenants.initialize(num_hosts=(num_leafs * num_hosts_per_leaf),
                                  max_vms_per_host=max_vms_per_host,
                                  num_tenants=num_tenants,
                                  min_vms=min_vms_per_tenant, max_vms=max_vms_per_tenant, vm_dist=vm_dist,
                                  num_groups=num_groups, min_group_size=min_group_size,
                                  group_size_dist=group_size_dist,
                                  multi_threaded=multi_threaded, num_threads=num_threads)

    _placement = placement.initialize(network=_network, tenants=_tenants, dist=placement_dist,
                                      num_bitmaps=num_bitmaps, generate_bitmaps=generate_bitmaps,
                                      multi_threaded=multi_threaded, num_threads=num_threads)

    _optimization = optimization.initialize(tenants=_tenants, placement=_placement, multi_threaded=multi_threaded,
                                            num_threads=num_threads)

    print('cloud: initialization complete!')

    return {'network': _network,
            'tenants': _tenants,
            'placement': _placement,
            'optimization': _optimization}
