import numpy as np
from simulation.cloud import *
from simulation.plot import *


np.random.seed(seed=0)

# cloud = Cloud(num_leafs=1056,
#               num_hosts_per_leaf=48,
#               max_vms_per_host=20,
#               num_tenants=3000,
#               min_vms_per_tenant=10,
#               max_vms_per_tenant=5000,
#               vm_dist='expon',
#               num_groups=100000,
#               min_group_size=5,
#               group_size_dist='uniform',
#               placement_dist='colocate',
#               colocate_num_hosts_per_leaf=20,
#               num_bitmaps=10,
#               generate_bitmaps=True,
#               use_all_bitmaps=True)

cloud = Cloud(num_leafs=576,
              num_hosts_per_leaf=48,
              num_rules_perf_leaf=1000,
              max_vms_per_host=20,
              num_tenants=3000,
              min_vms_per_tenant=10,
              max_vms_per_tenant=5000,
              vm_dist='expon',
              num_groups=100000,
              min_group_size=5,
              group_size_dist='uniform',
              placement_dist='colocate',
              colocate_num_hosts_per_leaf=48,
              num_bitmaps=10,
              generate_bitmaps=True,
              use_all_bitmaps=True,
              use_default_bitmap=True)

# cloud = Cloud(num_leafs=48,
#               num_hosts_per_leaf=48,
#               num_rules_perf_leaf=10,
#               max_vms_per_host=20,
#               num_tenants=100,
#               min_vms_per_tenant=10,
#               max_vms_per_tenant=1000,
#               vm_dist='expon',
#               num_groups=1000,
#               min_group_size=5,
#               group_size_dist='uniform',
#               placement_dist='colocate',
#               colocate_num_hosts_per_leaf=20,
#               num_bitmaps=2,
#               generate_bitmaps=True,
#               use_all_bitmaps=True,
#               use_default_bitmap=True)

data = Data(cloud)