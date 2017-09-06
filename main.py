import matplotlib.pyplot as plt
import json
import os
import seaborn as sb
from cloud import *

plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = (8, 6)
plt.rcParams['font.size'] = 14

# Statistical evaluation ...

cloud = Cloud(num_leafs=3,
              num_hosts_per_leaf=8,
              max_vms_per_host=20,
              num_tenants=100,
              min_vms_per_tenant=10,
              max_vms_per_tenant=20,
              vm_dist='expon',
              num_groups=100,
              min_group_size=5,
              group_size_dist='uniform',
              placement_dist='uniform')

# sb.kdeplot(tenants.groups_per_tenant_map, cumulative=True)
# plt.show()
