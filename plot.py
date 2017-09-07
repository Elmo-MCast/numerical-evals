import pandas as pd
import seaborn as sb


class Data:
    def __init__(self, cloud):
        self.cloud = cloud

        self.leafs_for_all_tenants = None
        self._get_leafs_for_all_tenants()

        self.percentage_hist_of_groups_covered_with_varying_bitmasks = None
        self._get_percentage_hist_of_groups_covered_with_varying_bitmasks()

    def _get_leafs_for_all_tenants(self):
        self.leafs_for_all_tenants = pd.Series()

        for t in range(self.cloud.tenants.num_tenants):
            self.leafs_for_all_tenants = self.leafs_for_all_tenants.append(
                self.cloud.placement.tenant_groups_to_leaf_count[t], ignore_index=True)

    def _get_percentage_hist_of_groups_covered_with_varying_bitmasks(self):
        hist = pd.cut(self.leafs_for_all_tenants, [i for i in range(self.cloud.num_bitmasks)]).value_counts()
        percentage_hist = hist / self.cloud.tenants.tenant_group_count_map.sum() * 100
        self.percentage_hist_of_groups_covered_with_varying_bitmasks = percentage_hist


class Plot:
    def __init__(self, plt, data):
        self.plt = plt
        self.data = data

    def cdf_leafs_for_all_tenants(self):
        ax = sb.kdeplot(self.data.leafs_for_all_tenants, cumulative=True)
        ax.set(xlabel='Leafs (all tenants)', ylabel='CDF')
        self.plt.show()

    def pdf_leafs_for_all_tenants(self):
        ax = self.data.leafs_for_all_tenants.plot(kind='density')
        ax.set(xlabel='Leafs (all tenants)', ylabel='PDF')
        self.plt.show()

    def cdf_groups_covered_with_varying_bitmasks(self):
        ax = sb.kdeplot(self.data.percentage_hist_of_groups_covered_with_varying_bitmasks, cumulative=True)
        ax.set(xlabel='Groups covered with <= %s bitmasks (all tenants)' % (self.data.cloud.num_bitmasks), ylabel='CDF')
        self.plt.show()
