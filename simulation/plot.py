import pandas as pd
import seaborn as sb


class Data:
    def __init__(self, cloud):
        self.network = cloud.data['network']
        self.tenants = cloud.data['tenants']
        self.tenants_maps = self.tenants['maps']
        self.placement = cloud.data['placement']

        self._get_leafs_for_all_tenants()
        self._get_percentage_hist_of_groups_covered_with_varying_bitmaps()
        self._get_rules_for_all_leafs()
        self._get_rules_for_all_leafs_post_optimization()
        self._get_redundancy_for_all_groups_in_all_tenants()
        self._get_rules_for_all_groups()
        self._get_rules_for_all_groups_post_optimization()
        self._get_leafs_to_rules_count()

        print('data: complete.')

    def _get_leafs_for_all_tenants(self):
        self.leafs_for_all_tenants = []

        for t in range(self.tenants['num_tenants']):
            for g in range(self.tenants_maps[t]['group_count']):
                self.leafs_for_all_tenants += [self.tenants_maps[t]['groups_map'][g]['leaf_count']]

        self.leafs_for_all_tenants = pd.Series(self.leafs_for_all_tenants)

    def _get_percentage_hist_of_groups_covered_with_varying_bitmaps(self):
        hist = pd.cut(self.leafs_for_all_tenants, [i for i in range(self.placement['num_bitmaps'] + 1)],
                      labels=[i for i in range(self.placement['num_bitmaps'])]).value_counts()
        percentage_hist = hist / self.tenants['group_count'] * 100
        self.percentage_hist_of_groups_covered_with_varying_bitmaps = percentage_hist.sort_index()

    def _get_rules_for_all_leafs(self):
        self.rules_for_all_leafs = [0] * self.network['num_leafs']

        for t in range(self.tenants['num_tenants']):
            for g in range(self.tenants_maps[t]['group_count']):
                if self.tenants_maps[t]['groups_map'][g]['leaf_count'] > self.placement['num_bitmaps']:
                    num_bitmaps = self.placement['num_bitmaps']
                    for l in self.tenants_maps[t]['groups_map'][g]['leafs']:
                        if num_bitmaps > 0:
                            num_bitmaps -= 1
                        else:
                            self.rules_for_all_leafs[l] += 1

        self.rules_for_all_leafs = pd.Series(self.rules_for_all_leafs)

    def _get_rules_for_all_leafs_post_optimization(self):
        self.rules_for_all_leafs_post_optimization = [0] * self.network['num_leafs']

        for t in range(self.tenants['num_tenants']):
            for g in range(self.tenants_maps[t]['group_count']):
                if self.tenants_maps[t]['groups_map'][g]['leaf_count'] > self.placement['num_bitmaps']:
                    for l in self.tenants_maps[t]['groups_map'][g]['leafs']:
                        if self.tenants_maps[t]['groups_map'][g]['leafs_map'][l]['has_rule']:
                            self.rules_for_all_leafs_post_optimization[l] += 1

        self.rules_for_all_leafs_post_optimization = pd.Series(self.rules_for_all_leafs_post_optimization)

    def _get_redundancy_for_all_groups_in_all_tenants(self):
        self.redundancy_for_all_groups_in_all_tenants = []

        for t in range(self.tenants['num_tenants']):
            for g in range(self.tenants_maps[t]['group_count']):
                if self.tenants_maps[t]['groups_map'][g]['leaf_count'] > self.placement['num_bitmaps']:
                    self.redundancy_for_all_groups_in_all_tenants += \
                        [self.tenants_maps[t]['groups_map'][g]['r'] /
                         (self.tenants_maps[t]['groups_map'][g]['r'] + self.tenants_maps[t]['groups_map'][g]['size'])
                         * 100]

        self.redundancy_for_all_groups_in_all_tenants = pd.Series(self.redundancy_for_all_groups_in_all_tenants)

    def _get_rules_for_all_groups(self):
        self.rules_for_all_groups = []

        for t in range(self.tenants['num_tenants']):
            for g in range(self.tenants_maps[t]['group_count']):
                self.rules_for_all_groups += [0]
                if self.tenants_maps[t]['groups_map'][g]['leaf_count'] > self.placement['num_bitmaps']:
                    for _ in self.tenants_maps[t]['groups_map'][g]['leafs']:
                        self.rules_for_all_groups[len(self.rules_for_all_groups) - 1] += 1

        self.rules_for_all_groups = pd.Series(self.rules_for_all_groups)

    def _get_rules_for_all_groups_post_optimization(self):
        self.rules_for_all_groups_post_optimization = []

        for t in range(self.tenants['num_tenants']):
            for g in range(self.tenants_maps[t]['group_count']):
                self.rules_for_all_groups_post_optimization += [0]
                if self.tenants_maps[t]['groups_map'][g]['leaf_count'] > self.placement['num_bitmaps']:
                    for l in self.tenants_maps[t]['groups_map'][g]['leafs']:
                        if self.tenants_maps[t]['groups_map'][g]['leafs_map'][l]['has_rule']:
                            self.rules_for_all_groups_post_optimization[len(self.rules_for_all_groups_post_optimization) - 1] += 1

        self.rules_for_all_groups_post_optimization = pd.Series(self.rules_for_all_groups_post_optimization)

    def _get_leafs_to_rules_count(self):
        self.leafs_to_rules_count = self.placement['maps']['leafs_to_rules_count']


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
                                    index=[i for i in range(1, self.data.placement['num_bitmaps'] + 1)])

        ax = cumulative_hist.plot()
        ax.set(xlabel='Number of bitmaps (max=%s)' % self.data.placement['num_bitmaps'],
               ylabel='Percentage of groups covered (all tenants)')
        self.plt.show()

    def cdf_rules_for_all_leafs(self):
        ax = sb.kdeplot(self.data.rules_for_all_leafs, cumulative=True)
        ax.set(xlabel="Number of rules using %s bitmaps (all leafs)" % self.data.placement['num_bitmaps'],
               ylabel='CDF')
        self.plt.show()

    def cdf_redundancy_for_all_groups_in_all_tenants(self):
        ax = sb.kdeplot(self.data.redundancy_for_all_groups_in_all_tenants, cumulative=True)
        ax.set(xlabel="Redundancy for all groups using %s bitmaps (all leafs)" % self.data.placement['num_bitmaps'],
               ylabel='CDF')
        self.plt.show()

    def hist_redundancy_for_all_groups_in_all_tenants(self):
        ax = self.data.redundancy_for_all_groups_in_all_tenants.plot(kind='hist')
        ax.set(
            xlabel="Redundancy for all groups using %s bitmaps (all leafs)" % self.data.placement['num_bitmaps'],
            ylabel='Frequency')
        self.plt.show()


class Log:
    def __init__(self, data, log_dir):
        self.data = data
        self.log_dir = log_dir

        self.log_rules_for_all_leafs()
        self.log_rules_for_all_leafs_post_optimization()
        self.log_rules_for_all_groups()
        self.log_rules_for_all_groups_post_optimization()
        self.log_redundancy_for_all_groups_in_all_tenants()

        print('log: complete.')

    def log_rules_for_all_leafs(self):
        self.data.rules_for_all_leafs.to_csv(self.log_dir + '/rules_for_all_leafs.csv')

    def log_rules_for_all_leafs_post_optimization(self):
        self.data.rules_for_all_leafs_post_optimization.to_csv(self.log_dir + '/rules_for_all_leafs_post_optimization.csv')

    def log_rules_for_all_groups(self):
        self.data.rules_for_all_groups.where(self.data.rules_for_all_groups > 0).dropna().to_csv(
            self.log_dir + '/rules_for_all_groups.csv')

    def log_rules_for_all_groups_post_optimization(self):
        self.data.rules_for_all_groups_post_optimization.where(self.data.rules_for_all_groups_post_optimization > 0).dropna().to_csv(
            self.log_dir + '/rules_for_all_groups_post_optimization.csv')

    def log_redundancy_for_all_groups_in_all_tenants(self):
        self.data.redundancy_for_all_groups_in_all_tenants.to_csv(
            self.log_dir + '/redundancy_for_all_groups_in_all_tenants.csv')
