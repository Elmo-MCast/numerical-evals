import pandas as pd
import seaborn as sb


def cdf_leafs_for_all_tenants(plt, data):
    ax = sb.kdeplot(data['leafs_for_all_tenants'], cumulative=True)
    ax.set(xlabel="Number of leafs per group (all tenants)", ylabel='CDF')
    plt.show()


def pdf_leafs_for_all_tenants(plt, data):
    ax = data['leafs_for_all_tenants'].plot(kind='density')
    ax.set(xlabel="Number of leafs per group (all tenants)", ylabel='PDF')
    plt.show()


def cdf_groups_covered_with_varying_bitmaps(plt, data):
    cumulative_hist = [0] * len(data['percentage_hist_of_groups_covered_with_varying_bitmaps'])

    for i, value in data['percentage_hist_of_groups_covered_with_varying_bitmaps'].iteritems():
        if i == 0:
            cumulative_hist[i] = value
        else:
            cumulative_hist[i] = value + cumulative_hist[i - 1]

    cumulative_hist = pd.Series(cumulative_hist,
                                index=[i for i in range(1, data['cloud']['placement']['num_bitmaps'] + 1)])

    ax = cumulative_hist.plot()
    ax.set(xlabel='Number of bitmaps (max=%s)' % data['cloud']['placement']['num_bitmaps'],
           ylabel='Percentage of groups covered (all tenants)')
    plt.show()


def cdf_rules_for_all_leafs(plt, data):
    ax = sb.kdeplot(data['rules_for_all_leafs'], cumulative=True)
    ax.set(xlabel="Number of rules using %s bitmaps (all leafs)" % data['cloud']['placement']['num_bitmaps'],
           ylabel='CDF')
    plt.show()


def cdf_redundancy_for_all_tenants(plt, data):
    ax = sb.kdeplot(data['redundancy_for_all_tenants'], cumulative=True)
    ax.set(xlabel="Redundancy for all groups using %s bitmaps (all leafs)" % data['cloud']['placement']['num_bitmaps'],
           ylabel='CDF')
    plt.show()


def hist_redundancy_for_all_tenants(plt, data):
    ax = data['redundancy_for_all_tenants'].plot(kind='hist')
    ax.set(
        xlabel="Redundancy for all groups using %s bitmaps (all leafs)" % data['cloud']['placement']['num_bitmaps'],
        ylabel='Frequency')
    plt.show()


def cdf_min_bitmaps_for_all_tenants(plt, data):
    ax = sb.kdeplot(data['min_bitmaps_for_all_tenants'], cumulative=True)
    ax.set(
        xlabel="Minimum bitmaps for all groups using %s bitmaps (all leafs)" % data['cloud']['placement']['num_bitmaps'],
        ylabel='CDF')
    plt.show()


def pdf_min_bitmaps_for_all_tenants(plt, data):
    ax = data['min_bitmaps_for_all_tenants'].plot(kind='density')
    ax.set(
        xlabel="Minimum bitmaps for all groups using %s bitmaps (all leafs)" % data['cloud']['placement']['num_bitmaps'],
        ylabel='PDF')
    plt.show()


def hist_min_bitmaps_for_all_tenants(plt, data):
    ax = data['min_bitmaps_for_all_tenants'].plot(kind='hist')
    ax.set(
        xlabel="Minimum bitmaps for all groups using %s bitmaps (all leafs)" % data['cloud']['placement']['num_bitmaps'],
        ylabel='Frequency')
    plt.show()
