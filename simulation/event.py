import random
from simulation.algorithms import algorithms


# VM_TYPES = ['P',  # publisher
#             'S',  # subscriber
#             'B'   # Both
#             ]
# EVENT_TYPES = ['J',  # Join
#                'L'   # Leave
#                ]

class Event:
    def __init__(self, switch_event_types_to_update_count_map, switch_event_types_to_group_size_map, vms_map, algorithm,
                 leafs_to_rules_count_map, num_bitmaps, num_leafs_per_bitmap, redundancy_per_bitmap, num_rules_per_leaf,
                 probability, group, min_group_size, vm_count, num_hosts_per_leaf):
        self.virtual_switch_event_types_to_update_count_map = switch_event_types_to_update_count_map['virtual']
        self.leaf_switch_event_types_to_update_count_map = switch_event_types_to_update_count_map['leaf']
        self.switch_event_types_to_group_size_map = switch_event_types_to_group_size_map
        self.vms_map = vms_map
        self.algorithm = algorithm
        self.leafs_to_rules_count_map = leafs_to_rules_count_map
        self.num_bitmaps = num_bitmaps
        self.num_leafs_per_bitmap = num_leafs_per_bitmap
        self.redundancy_per_bitmap = redundancy_per_bitmap
        self.num_rules_per_leaf = num_rules_per_leaf
        self.probability = probability
        self.group = group
        self.min_group_size = min_group_size
        self.vm_count = vm_count
        self.num_hosts_per_leaf = num_hosts_per_leaf

        self._run()

    def _run(self):
        event_count = self.group['event_count']
        vms = self.group['vms']
        vms_types = self.group['vms_types']
        leafs_map = self.group['leafs_map']
        for _ in range(event_count):
            size = self.group['size']

            # Get event type
            if size == self.min_group_size:
                event_type = 'J'
            elif size == self.vm_count:
                event_type = 'L'
            else:
                event_type = random.sample(['J', 'L'], 1)[0]

            self.virtual_switch_event_types_to_update_count_map[event_type] += [0]
            self.leaf_switch_event_types_to_update_count_map[event_type] += [0]
            virtual_switch_event_type_to_update_count_map = \
                self.virtual_switch_event_types_to_update_count_map[event_type]
            leaf_switch_event_type_to_update_count_map = \
                self.leaf_switch_event_types_to_update_count_map[event_type]
            switch_event_type_to_group_size_map = self.switch_event_types_to_group_size_map[event_type]

            if event_type == 'J':  # Process join event
                # Select a random VM to add
                vm = random.sample(set(range(self.vm_count)) - set(vms), 1)[0]
                vm_type = random.sample(['P', 'S', 'B'], 1)[0]
                vms += [vm]
                vms_types[vm] = vm_type
                size += 1
                self.group['size'] = size
                switch_event_type_to_group_size_map += [size]

                if vm_type == 'P':
                    virtual_switch_event_type_to_update_count_map[-1] += 1
                else:
                    vm_map = self.vms_map[vm]
                    vm_leaf, vm_host = vm_map['leaf'], vm_map['host']
                    if vm_leaf in leafs_map:
                        leaf_map = leafs_map[vm_leaf]
                        leaf_map['bitmap'] |= 1 << (vm_host % self.num_hosts_per_leaf)
                    else:
                        leaf_map = dict()
                        leaf_map['bitmap'] = 1 << (vm_host % self.num_hosts_per_leaf)
                        leafs_map[vm_leaf] = leaf_map

                    leafs_with_rule = []
                    for l in leafs_map:
                        leaf_map = leafs_map[l]
                        if 'has_rule' in leaf_map:
                            leafs_with_rule += [l]
                            self.leafs_to_rules_count_map[l] -= 1
                            del leaf_map['has_rule']
                        elif 'has_bitmap' in leaf_map:
                            del leaf_map['has_bitmap']
                        if '~bitmap' in leaf_map:
                            del leaf_map['~bitmap']
                    if 'default_bitmap' in self.group:
                        del self.group['default_bitmap']

                    algorithms.run(
                        algorithm=self.algorithm,
                        group=self.group,
                        max_bitmaps=self.num_bitmaps,
                        max_leafs_per_bitmap=self.num_leafs_per_bitmap,
                        redundancy_per_bitmap=self.redundancy_per_bitmap,
                        leafs_to_rules_count_map=self.leafs_to_rules_count_map,
                        max_rules_per_leaf=self.num_rules_per_leaf,
                        probability=self.probability)

                    for l in leafs_map:
                        leaf_map = leafs_map[l]
                        if 'has_rule' in leaf_map:
                            if (l == vm_leaf) or (l not in leafs_with_rule):
                                leaf_switch_event_type_to_update_count_map[-1] += 1
                        else:
                            if l in leafs_with_rule:
                                leaf_switch_event_type_to_update_count_map[-1] += 1

                    if vm_type == 'S':
                        virtual_switch_event_type_to_update_count_map[-1] += 1

                    virtual_switch_event_type_to_update_count_map[-1] += sum(
                        [1 for vm in vms if vms_types[vm] == 'P' or vms_types[vm] == 'B'])
            else:  # Process leave event
                # Select a random VM to remove
                vm = random.sample(vms, 1)[0]
                vm_type = vms_types[vm]
                vms.remove(vm)
                del vms_types[vm]
                switch_event_type_to_group_size_map += [size]
                size -= 1
                self.group['size'] = size

                if vm_type == 'P':
                    virtual_switch_event_type_to_update_count_map[-1] += 1
                else:
                    vm_map = self.vms_map[vm]
                    vm_leaf, vm_host = vm_map['leaf'], vm_map['host']
                    leaf_map = leafs_map[vm_leaf]
                    leaf_map['bitmap'] &= ~(1 << (vm_host % self.num_hosts_per_leaf))

                    leafs_with_rule = []
                    for l in leafs_map:
                        leaf_map = leafs_map[l]
                        if 'has_rule' in leaf_map:
                            leafs_with_rule += [l]
                            self.leafs_to_rules_count_map[l] -= 1
                            del leaf_map['has_rule']
                        elif 'has_bitmap' in leaf_map:
                            del leaf_map['has_bitmap']
                        if '~bitmap' in leaf_map:
                            del leaf_map['~bitmap']
                    if 'default_bitmap' in self.group:
                        del self.group['default_bitmap']

                    algorithms.run(
                        algorithm=self.algorithm,
                        group=self.group,
                        max_bitmaps=self.num_bitmaps,
                        max_leafs_per_bitmap=self.num_leafs_per_bitmap,
                        redundancy_per_bitmap=self.redundancy_per_bitmap,
                        leafs_to_rules_count_map=self.leafs_to_rules_count_map,
                        max_rules_per_leaf=self.num_rules_per_leaf,
                        probability=self.probability)

                    for l in leafs_map:
                        leaf_map = leafs_map[l]
                        if 'has_rule' in leaf_map:
                            if (l == vm_leaf) or (l not in leafs_with_rule):
                                leaf_switch_event_type_to_update_count_map[-1] += 1
                        else:
                            if l in leafs_with_rule:
                                leaf_switch_event_type_to_update_count_map[-1] += 1

                    virtual_switch_event_type_to_update_count_map[-1] += 1
                    virtual_switch_event_type_to_update_count_map[-1] += sum(
                        [1 for vm in vms if vms_types[vm] == 'P' or vms_types[vm] == 'B'])

