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
        self.data.rules_for_all_leafs_post_optimization.to_csv(
            self.log_dir + '/rules_for_all_leafs_post_optimization.csv')

    def log_rules_for_all_groups(self):
        self.data.rules_for_all_groups.where(self.data.rules_for_all_groups > 0).dropna().to_csv(
            self.log_dir + '/rules_for_all_groups.csv')

    def log_rules_for_all_groups_post_optimization(self):
        self.data.rules_for_all_groups_post_optimization.where(
            self.data.rules_for_all_groups_post_optimization > 0).dropna().to_csv(
            self.log_dir + '/rules_for_all_groups_post_optimization.csv')

    def log_redundancy_for_all_groups_in_all_tenants(self):
        self.data.redundancy_for_all_groups_in_all_tenants.to_csv(
            self.log_dir + '/redundancy_for_all_groups_in_all_tenants.csv')
