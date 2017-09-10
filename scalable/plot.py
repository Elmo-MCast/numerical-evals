import seaborn as sb

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

    def cdf_groups_covered_with_varying_bitmaps(self):
        cumulative_hist = [0] * len(self.data.percentage_hist_of_groups_covered_with_varying_bitmaps)

        for i, value in self.data.percentage_hist_of_groups_covered_with_varying_bitmaps.iteritems():
            if i == 0:
                cumulative_hist[i] = value
            else:
                cumulative_hist[i] = value + cumulative_hist[i - 1]

        cumulative_hist = pd.Series(cumulative_hist,
                                    index=[i for i in range(1, self.data.cloud.placement.num_bitmaps + 1)])

        ax = cumulative_hist.plot()
        ax.set(xlabel='Number of bitmaps (max=%s)' % self.data.cloud.placement.num_bitmaps,
               ylabel='Percentage of groups covered (all tenants)')
        self.plt.show()

    def cdf_rules_for_all_leafs(self):
        ax = sb.kdeplot(self.data.rules_for_all_leafs, cumulative=True)
        ax.set(xlabel="Number of rules using %s bitmaps (all leafs)" % self.data.cloud.placement.num_bitmaps,
               ylabel='CDF')
        self.plt.show()

    def cdf_redundancy_for_all_tenants(self):
        ax = sb.kdeplot(self.data.redundancy_for_all_tenants, cumulative=True)
        ax.set(xlabel="Redundancy for all groups using %s bitmaps (all leafs)" % self.data.cloud.placement.num_bitmaps,
               ylabel='CDF')
        self.plt.show()

    def hist_redundancy_for_all_tenants(self):
        ax = self.data.redundancy_for_all_tenants.plot(kind='hist')
        ax.set(
            xlabel="Redundancy for all groups using %s bitmaps (all leafs)" % self.data.cloud.placement.num_bitmaps,
            ylabel='Frequency')
        self.plt.show()

    def cdf_min_bitmaps_for_all_tenants(self):
        ax = sb.kdeplot(self.data.min_bitmaps_for_all_tenants, cumulative=True)
        ax.set(
            xlabel="Minimum bitmaps for all groups using %s bitmaps (all leafs)" % self.data.cloud.placement.num_bitmaps,
            ylabel='CDF')
        self.plt.show()

    def pdf_min_bitmaps_for_all_tenants(self):
        ax = self.data.min_bitmaps_for_all_tenants.plot(kind='density')
        ax.set(
            xlabel="Minimum bitmaps for all groups using %s bitmaps (all leafs)" % self.data.cloud.placement.num_bitmaps,
            ylabel='PDF')
        self.plt.show()

    def hist_min_bitmaps_for_all_tenants(self):
        ax = self.data.min_bitmaps_for_all_tenants.plot(kind='hist')
        ax.set(
            xlabel="Minimum bitmaps for all groups using %s bitmaps (all leafs)" % self.data.cloud.placement.num_bitmaps,
            ylabel='Frequency')
        self.plt.show()
