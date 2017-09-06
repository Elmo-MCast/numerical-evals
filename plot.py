import pandas as pd
import seaborn as sb
import matplotlib


class Data:
    def __init__(self, cloud):
        self.cloud = cloud

        self.leafs_for_all_tenants = None
        self._get_leafs_for_all_tenants()

    def _get_leafs_for_all_tenants(self):
        self.leafs_for_all_tenants = pd.Series()

        for i in range(self.cloud.tenants.num_tenants):
            self.leafs_for_all_tenants = self.leafs_for_all_tenants.append(
                self.cloud.placement.tenant_group_to_leaf_count[i], ignore_index=True)


class Plot:
    def __init__(self, plt, data):
        self.plt = plt
        self.data = data

    def cdf_leafs_for_all_tenants(self):
        ax = sb.kdeplot(self.data.leafs_for_all_tenants, cumulative=True)
        ax.set(xlabel='Leafs (all tenants)', ylabel='CDF')
        self.plt.show()