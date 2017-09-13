from multi_threading.plot import Data

from archive.multi_threading.cloud import *

# Statistical evaluation ...

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
#               placement_dist='colocate')

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
#               placement_dist='uniform',
#               num_bitmaps=32,
#               generate_bitmaps=True,
#               multi_threaded=True,
#               num_threads=8)

# cloud = Cloud(num_leafs=48,
#               num_hosts_per_leaf=48,
#               max_vms_per_host=20,
#               num_tenants=100,
#               min_vms_per_tenant=10,
#               max_vms_per_tenant=100,
#               vm_dist='expon-mean',
#               num_groups=1000,
#               min_group_size=5,
#               group_size_dist='uniform',
#               placement_dist='uniform')

cloud = Cloud(num_leafs=48,
              num_hosts_per_leaf=48,
              max_vms_per_host=20,
              num_tenants=100,
              min_vms_per_tenant=10,
              max_vms_per_tenant=100,
              vm_dist='expon',
              num_groups=1000,
              min_group_size=5,
              group_size_dist='uniform',
              placement_dist='uniform',
              num_bitmaps=10,
              generate_bitmaps=True,
              multi_threaded=False,
              num_threads=4)

data = Data(cloud)

# cloud = Cloud(num_leafs=48,
#               num_hosts_per_leaf=48,
#               max_vms_per_host=20,
#               num_tenants=100,
#               min_vms_per_tenant=10,
#               max_vms_per_tenant=100,
#               vm_dist='expon',
#               num_groups=1000,
#               min_group_size=5,
#               group_size_dist='uniform',
#               placement_dist='colocate')
