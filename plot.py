import pandas as pd
import seaborn as sb


class Data:
    def __init__(self, cloud):
        self.cloud = cloud

        self.leafs_for_all_tenants = None
        self._get_leafs_for_all_tenants()

        self.percentage_hist_of_groups_covered_with_varying_bitmasks = None
        self._get_percentage_hist_of_groups_covered_with_varying_bitmasks()

        self.rules_for_all_leafs = None
        self._get_rules_for_all_leafs()

    def _get_leafs_for_all_tenants(self):
        self.leafs_for_all_tenants = pd.Series()

        for t in range(self.cloud.tenants.num_tenants):
            self.leafs_for_all_tenants = self.leafs_for_all_tenants.append(
                self.cloud.placement.tenant_groups_to_leaf_count[t], ignore_index=True)

    def _get_percentage_hist_of_groups_covered_with_varying_bitmasks(self):
        hist = pd.cut(self.leafs_for_all_tenants, [i for i in range(self.cloud.placement.num_bitmasks + 1)],
                      labels=[i for i in range(self.cloud.placement.num_bitmasks)]).value_counts()
        percentage_hist = hist / self.cloud.tenants.tenant_group_count_map.sum() * 100
        self.percentage_hist_of_groups_covered_with_varying_bitmasks = percentage_hist.sort_index()

    def _get_rules_for_all_leafs(self):
        self.rules_for_all_leafs = [0] * self.cloud.network.num_leafs

        for t in range(self.cloud.tenants.num_tenants):
            for g in range(self.cloud.tenants.tenant_group_count_map[t]):
                if self.cloud.placement.tenant_groups_to_leaf_count[t][g] > self.cloud.placement.num_bitmasks:
                    for l in self.cloud.placement.tenant_groups_to_leafs_map[t][g]:
                        self.rules_for_all_leafs[l] += 1

        self.rules_for_all_leafs = pd.Series(self.rules_for_all_leafs)

class Plot:
    def __init__(self, plt, data):
        self.plt = plt
        self.data = data

    def cdf_leafs_for_all_tenants(self):
        ax = sb.kdeplot(self.data.leafs_for_all_tenants, cumulative=True)
        ax.set(xlabel="Number of leafs per group (all tenants)", ylabel='CDF')
        self.plt.show()

    def pdf_leafs_for_all_tenants(self):
        ax = self.data.leafs_for_all_tenants.plot(kind='density')
        ax.set(xlabel="Number of leafs per group (all tenants)", ylabel='PDF')
        self.plt.show()

    def cdf_groups_covered_with_varying_bitmasks(self):
        cumulative_hist = [0] * len(self.data.percentage_hist_of_groups_covered_with_varying_bitmasks)

        for i, value in self.data.percentage_hist_of_groups_covered_with_varying_bitmasks.iteritems():
            if i == 0:
                cumulative_hist[i] = value
            else:
                cumulative_hist[i] = value + cumulative_hist[i - 1]

        cumulative_hist = pd.Series(cumulative_hist,
                                    index=[i for i in range(1, self.data.cloud.placement.num_bitmasks + 1)])

        ax = cumulative_hist.plot()
        ax.set(xlabel='Number of bitmasks (max=%s)' % self.data.cloud.placement.num_bitmasks,
               ylabel='Percentage of groups covered (all tenants)')
        self.plt.show()

    def cdf_rules_for_all_leafs(self):
        ax = sb.kdeplot(self.data.rules_for_all_leafs, cumulative=True)
        ax.set(xlabel="Number of rules using %s bitmasks (all leafs)" % self.data.cloud.placement.num_bitmasks,
               ylabel='CDF')
        self.plt.show()