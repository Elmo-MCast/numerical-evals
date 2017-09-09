from threading import Thread
import operator
from functools import reduce
import pandas as pd
import numpy as np
from bitstring import BitArray


class Placement:
    def __init__(self, network, tenants, dist='uniform', num_bitmaps=32, generate_bitmaps=False,
                 multi_threaded=True, num_threads=2):
        self.dist = dist
        self.network = network
        self.tenants = tenants
        self.num_bitmaps = num_bitmaps
        self.multi_threaded = multi_threaded
        self.num_threads = num_threads

        if self.multi_threaded:
            self.num_chunks = self.num_threads
            if self.tenants.num_tenants % self.num_chunks != 0:
                raise Exception("number of threads should be a multiple of tenants count")
            self.chunk_size = int(self.tenants.num_tenants / self.num_chunks)

            # print('placement: no. of chunks %s' % self.num_chunks)

        self.tenant_vms_to_host_map = None
        self._get_tenant_vms_to_host_map()

        self.tenant_vms_to_leaf_map = None
        self._get_tenant_vms_to_leaf_map()

        self.tenant_groups_to_leafs_map = None
        self._get_tenant_groups_to_leafs_map()

        self.tenant_groups_to_leaf_count = None
        self._get_tenant_groups_to_leaf_count()

        if generate_bitmaps:
            self.tenant_groups_leafs_to_hosts_map = None
            self._get_tenant_groups_leafs_to_hosts_map()

            self.tenant_groups_leafs_to_bitmap_map = None
            self._get_tenant_groups_leafs_to_bitmap_map()

        print('placement: initialized.')

    def _get_tenant_vms_to_host_map(self):
        if self.dist == 'uniform':
            self.tenant_vms_to_host_map = [None] * self.tenants.num_tenants
            available_hosts = [h for h in range(self.tenants.num_hosts)]
            selected_hosts_count = [0] * self.tenants.num_hosts

            for t in range(self.tenants.num_tenants):
                self.tenant_vms_to_host_map[t] = pd.Series(
                    np.random.choice(a=available_hosts,
                                     size=self.tenants.tenant_vm_count_map[t], replace=False))

                for _, host in self.tenant_vms_to_host_map[t].iteritems():
                    selected_hosts_count[host] += 1

                max_host_count = max(selected_hosts_count)
                if max_host_count == self.tenants.max_vms_per_host:
                    removed_hosts = [h for h, host_count in enumerate(selected_hosts_count)
                                     if host_count == max_host_count]
                    available_hosts = list(set(available_hosts) - set(removed_hosts))
                    for removed_host in sorted(removed_hosts, reverse=True):
                        selected_hosts_count[removed_host] = -1
        elif self.dist == 'colocate':
            self.tenant_vms_to_host_map = [None] * self.tenants.num_tenants
            available_leafs = [l for l in range(self.network.num_leafs)]

            available_hosts_per_leaf = [None] * self.network.num_leafs
            selected_hosts_count_per_leaf = [None] * self.network.num_leafs
            for l in range(self.network.num_leafs):
                available_hosts_per_leaf[l] = [(l * self.network.num_hosts_per_leaf) + h
                                               for h in range(self.network.num_hosts_per_leaf)]
                selected_hosts_count_per_leaf[l] = [0] * self.network.num_hosts_per_leaf

            for t in range(self.tenants.num_tenants):
                self.tenant_vms_to_host_map[t] = pd.Series([None] * self.tenants.tenant_vm_count_map[t])

                running_index = 0
                running_count = self.tenants.tenant_vm_count_map[t]
                while running_count > 0:
                    selected_leaf = np.random.choice(a=available_leafs, size=1)[0]
                    selected_leaf_hosts_count = len(available_hosts_per_leaf[selected_leaf])

                    if int(running_count / selected_leaf_hosts_count) > 0:
                        for h in range(selected_leaf_hosts_count):
                            self.tenant_vms_to_host_map[t][running_index] = available_hosts_per_leaf[selected_leaf][h]
                            selected_hosts_count_per_leaf[selected_leaf][h] += 1
                            running_index += 1
                        running_count -= selected_leaf_hosts_count
                    else:
                        for h in range(running_count):
                            self.tenant_vms_to_host_map[t][running_index] = available_hosts_per_leaf[selected_leaf][h]
                            selected_hosts_count_per_leaf[selected_leaf][h] += 1
                            running_index += 1
                        running_count = 0

                    max_host_count = max(selected_hosts_count_per_leaf[selected_leaf])
                    if max_host_count == self.tenants.max_vms_per_host:
                        removed_hosts = [h for h, host_count in enumerate(selected_hosts_count_per_leaf[selected_leaf])
                                         if host_count == max_host_count]
                        for removed_host in sorted(removed_hosts, reverse=True):
                            del available_hosts_per_leaf[selected_leaf][removed_host]
                            del selected_hosts_count_per_leaf[selected_leaf][removed_host]

                        if len(available_hosts_per_leaf[selected_leaf]) == 0:
                            available_leafs.remove(selected_leaf)
        else:
            raise (Exception("invalid dist parameter for vm to host allocation"))

    def _get_tenant_vms_to_leaf_map_chunk(self, tenant_vms_to_leaf_map_chunks, chunk_id, chunk_size):
        base_index = chunk_id * chunk_size
        tenant_vms_to_leaf_map = [None] * chunk_size

        for t in range(base_index, base_index + chunk_size):
            tenant_vms_to_leaf_map[t % chunk_size] = pd.Series(
                [self.network.host_to_leaf_map[host] for _, host in self.tenant_vms_to_host_map[t].iteritems()])

        tenant_vms_to_leaf_map_chunks[chunk_id] = tenant_vms_to_leaf_map

    def _get_tenant_vms_to_leaf_map(self):
        if not self.multi_threaded:
            self.tenant_vms_to_leaf_map = [None] * self.tenants.num_tenants

            for t in range(self.tenants.num_tenants):
                self.tenant_vms_to_leaf_map[t] = pd.Series([self.network.host_to_leaf_map[host]
                                                            for _, host in self.tenant_vms_to_host_map[t].iteritems()])
        else:
            tenant_vms_to_leaf_map_chunks = [None] * self.num_chunks
            tenant_vms_to_leaf_map_threads = [None] * self.num_chunks

            for i in range(self.num_chunks):
                tenant_vms_to_leaf_map_threads[i] = Thread(target=self._get_tenant_vms_to_leaf_map_chunk,
                                                           args=(tenant_vms_to_leaf_map_chunks, i, self.chunk_size))
                tenant_vms_to_leaf_map_threads[i].start()

            for i in range(self.num_chunks):
                tenant_vms_to_leaf_map_threads[i].join()

            self.tenant_vms_to_leaf_map = reduce(operator.concat, tenant_vms_to_leaf_map_chunks)

    def _get_tenant_groups_to_leafs_map_chunk(self, tenant_groups_to_leafs_map_chunks, chunk_id, chunk_size):
        base_index = chunk_id * chunk_size
        tenant_groups_to_leafs_map = [None] * chunk_size

        for t in range(base_index, base_index + chunk_size):
            _groups_to_leaf_map = [None] * self.tenants.tenant_group_count_map[t]

            for g in range(self.tenants.tenant_group_count_map[t]):
                _groups_to_leaf_map[g] = pd.Series(list(
                    {self.tenant_vms_to_leaf_map[t][vm]
                     for _, vm in self.tenants.tenant_groups_to_vms_map[t][g].iteritems()}))
            tenant_groups_to_leafs_map[t % chunk_size] = _groups_to_leaf_map

        tenant_groups_to_leafs_map_chunks[chunk_id] = tenant_groups_to_leafs_map

    def _get_tenant_groups_to_leafs_map(self):
        if not self.multi_threaded:
            self.tenant_groups_to_leafs_map = [None] * self.tenants.num_tenants

            for t in range(self.tenants.num_tenants):
                _groups_to_leaf_map = [None] * self.tenants.tenant_group_count_map[t]

                for g in range(self.tenants.tenant_group_count_map[t]):
                    _groups_to_leaf_map[g] = pd.Series(list(
                        {self.tenant_vms_to_leaf_map[t][vm]
                         for _, vm in self.tenants.tenant_groups_to_vms_map[t][g].iteritems()}))
                self.tenant_groups_to_leafs_map[t] = _groups_to_leaf_map
        else:
            tenant_groups_to_leafs_map_chunks = [None] * self.num_chunks
            tenant_groups_to_leafs_map_threads = [None] * self.num_chunks

            for i in range(self.num_chunks):
                tenant_groups_to_leafs_map_threads[i] = Thread(
                    target=self._get_tenant_groups_to_leafs_map_chunk,
                    args=(tenant_groups_to_leafs_map_chunks, i, self.chunk_size))
                tenant_groups_to_leafs_map_threads[i].start()

            for i in range(self.num_chunks):
                tenant_groups_to_leafs_map_threads[i].join()

            self.tenant_groups_to_leafs_map = reduce(operator.concat, tenant_groups_to_leafs_map_chunks)

    def _get_tenant_groups_to_leaf_count_chunk(self, tenant_groups_to_leaf_count_chunks, chunk_id, chunk_size):
        base_index = chunk_id * chunk_size
        tenant_groups_to_leaf_count = [None] * chunk_size

        for t in range(base_index, base_index + chunk_size):
            _groups_to_leaf_count = [None] * self.tenants.tenant_group_count_map[t]

            for g in range(self.tenants.tenant_group_count_map[t]):
                _groups_to_leaf_count[g] = len(self.tenant_groups_to_leafs_map[t][g])

            tenant_groups_to_leaf_count[t % chunk_size] = pd.Series(_groups_to_leaf_count)

        tenant_groups_to_leaf_count_chunks[chunk_id] = tenant_groups_to_leaf_count

    def _get_tenant_groups_to_leaf_count(self):
        if not self.multi_threaded:
            self.tenant_groups_to_leaf_count = [None] * self.tenants.num_tenants

            for t in range(self.tenants.num_tenants):
                _groups_to_leaf_count = [None] * self.tenants.tenant_group_count_map[t]

                for g in range(self.tenants.tenant_group_count_map[t]):
                    _groups_to_leaf_count[g] = len(self.tenant_groups_to_leafs_map[t][g])

                self.tenant_groups_to_leaf_count[t] = pd.Series(_groups_to_leaf_count)
        else:
            tenant_groups_to_leaf_count_chunks = [None] * self.num_chunks
            tenant_groups_to_leaf_count_threads = [None] * self.num_chunks

            for i in range(self.num_chunks):
                tenant_groups_to_leaf_count_threads[i] = Thread(
                    target=self._get_tenant_groups_to_leaf_count_chunk,
                    args=(tenant_groups_to_leaf_count_chunks, i, self.chunk_size))
                tenant_groups_to_leaf_count_threads[i].start()

            for i in range(self.num_chunks):
                tenant_groups_to_leaf_count_threads[i].join()

            self.tenant_groups_to_leaf_count = reduce(operator.concat, tenant_groups_to_leaf_count_chunks)

    def _get_tenant_groups_leafs_to_hosts_map_chunk(self, tenant_groups_leafs_to_hosts_map_chunks,
                                                    chunk_id, chunk_size):
        base_index = chunk_id * chunk_size
        tenant_groups_leafs_to_hosts_map = [None] * chunk_size

        for t in range(base_index, base_index + chunk_size):
            _groups_leafs_to_hosts_map = [None] * self.tenants.tenant_group_count_map[t]

            for g in range(self.tenants.tenant_group_count_map[t]):
                _leafs_to_hosts_dict = dict()

                if self.tenant_groups_to_leaf_count[t][g] > self.num_bitmaps:
                    for _, vm in self.tenants.tenant_groups_to_vms_map[t][g].iteritems():
                        if self.tenant_vms_to_leaf_map[t][vm] in _leafs_to_hosts_dict:
                            _leafs_to_hosts_dict[self.tenant_vms_to_leaf_map[t][vm]] |= {
                                self.tenant_vms_to_host_map[t][vm]}
                        else:
                            _leafs_to_hosts_dict[self.tenant_vms_to_leaf_map[t][vm]] = {
                                self.tenant_vms_to_host_map[t][vm]}

                _groups_leafs_to_hosts_map[g] = _leafs_to_hosts_dict

            tenant_groups_leafs_to_hosts_map[t % chunk_size] = _groups_leafs_to_hosts_map

        tenant_groups_leafs_to_hosts_map_chunks[chunk_id] = tenant_groups_leafs_to_hosts_map

    def _get_tenant_groups_leafs_to_hosts_map(self):
        if not self.multi_threaded:
            self.tenant_groups_leafs_to_hosts_map = [None] * self.tenants.num_tenants

            for t in range(self.tenants.num_tenants):
                _groups_leafs_to_hosts_map = [None] * self.tenants.tenant_group_count_map[t]

                for g in range(self.tenants.tenant_group_count_map[t]):
                    _leafs_to_hosts_dict = dict()

                    if self.tenant_groups_to_leaf_count[t][g] > self.num_bitmaps:
                        for _, vm in self.tenants.tenant_groups_to_vms_map[t][g].iteritems():
                            if self.tenant_vms_to_leaf_map[t][vm] in _leafs_to_hosts_dict:
                                _leafs_to_hosts_dict[self.tenant_vms_to_leaf_map[t][vm]] |= {
                                    self.tenant_vms_to_host_map[t][vm]}
                            else:
                                _leafs_to_hosts_dict[self.tenant_vms_to_leaf_map[t][vm]] = {
                                    self.tenant_vms_to_host_map[t][vm]}

                    _groups_leafs_to_hosts_map[g] = _leafs_to_hosts_dict

                self.tenant_groups_leafs_to_hosts_map[t] = _groups_leafs_to_hosts_map
        else:
            tenant_groups_leafs_to_hosts_map_chunks = [None] * self.num_chunks
            tenant_groups_leafs_to_hosts_map_threads = [None] * self.num_chunks

            for i in range(self.num_chunks):
                tenant_groups_leafs_to_hosts_map_threads[i] = Thread(
                    target=self._get_tenant_groups_leafs_to_hosts_map_chunk,
                    args=(tenant_groups_leafs_to_hosts_map_chunks, i, self.chunk_size))
                tenant_groups_leafs_to_hosts_map_threads[i].start()

            for i in range(self.num_chunks):
                tenant_groups_leafs_to_hosts_map_threads[i].join()

            self.tenant_groups_leafs_to_hosts_map = reduce(operator.concat, tenant_groups_leafs_to_hosts_map_chunks)

    def _get_tenant_groups_leafs_to_bitmap_map_chunk(self, tenant_groups_leafs_to_bitmap_map_chunks,
                                                     chunk_id, chunk_size):
        base_index = chunk_id * chunk_size
        tenant_groups_leafs_to_bitmap_map = [None] * chunk_size

        for t in range(base_index, base_index + chunk_size):
            _groups_leafs_to_bitmap_map = [None] * self.tenants.tenant_group_count_map[t]

            for g in range(self.tenants.tenant_group_count_map[t]):
                _leafs_to_bitmap_dict = dict()

                if self.tenant_groups_to_leaf_count[t][g] > self.num_bitmaps:
                    for l in self.tenant_groups_leafs_to_hosts_map[t][g]:
                        _leafs_to_bitmap_dict[l] = dict()

                        _leafs_to_bitmap_dict[l]['actual'] = BitArray(self.network.num_hosts_per_leaf)
                        for h in self.tenant_groups_leafs_to_hosts_map[t][g][l]:
                            _leafs_to_bitmap_dict[l]['actual'][h % self.network.num_hosts_per_leaf] = 1

                        _leafs_to_bitmap_dict[l]['sorted'] = BitArray(
                            sorted(_leafs_to_bitmap_dict[l]['actual'], reverse=True))

                _groups_leafs_to_bitmap_map[g] = _leafs_to_bitmap_dict

            tenant_groups_leafs_to_bitmap_map[t % chunk_size] = _groups_leafs_to_bitmap_map

        tenant_groups_leafs_to_bitmap_map_chunks[chunk_id] = tenant_groups_leafs_to_bitmap_map

    def _get_tenant_groups_leafs_to_bitmap_map(self):
        if not self.multi_threaded:
            self.tenant_groups_leafs_to_bitmap_map = [None] * self.tenants.num_tenants

            for t in range(self.tenants.num_tenants):
                _groups_leafs_to_bitmap_map = [None] * self.tenants.tenant_group_count_map[t]

                for g in range(self.tenants.tenant_group_count_map[t]):
                    _leafs_to_bitmap_dict = dict()

                    if self.tenant_groups_to_leaf_count[t][g] > self.num_bitmaps:
                        for l in self.tenant_groups_leafs_to_hosts_map[t][g]:
                            _leafs_to_bitmap_dict[l] = dict()

                            _leafs_to_bitmap_dict[l]['actual'] = BitArray(self.network.num_hosts_per_leaf)
                            for h in self.tenant_groups_leafs_to_hosts_map[t][g][l]:
                                _leafs_to_bitmap_dict[l]['actual'][h % self.network.num_hosts_per_leaf] = 1

                            _leafs_to_bitmap_dict[l]['sorted'] = BitArray(
                                sorted(_leafs_to_bitmap_dict[l]['actual'], reverse=True))

                    _groups_leafs_to_bitmap_map[g] = _leafs_to_bitmap_dict

                self.tenant_groups_leafs_to_bitmap_map[t] = _groups_leafs_to_bitmap_map
        else:
            tenant_groups_leafs_to_bitmap_map_chunks = [None] * self.num_chunks
            tenant_groups_leafs_to_bitmap_map_threads = [None] * self.num_chunks

            for i in range(self.num_chunks):
                tenant_groups_leafs_to_bitmap_map_threads[i] = Thread(
                    target=self._get_tenant_groups_leafs_to_bitmap_map_chunk,
                    args=(tenant_groups_leafs_to_bitmap_map_chunks, i, self.chunk_size))
                tenant_groups_leafs_to_bitmap_map_threads[i].start()

            for i in range(self.num_chunks):
                tenant_groups_leafs_to_bitmap_map_threads[i].join()

            self.tenant_groups_leafs_to_bitmap_map = reduce(operator.concat, tenant_groups_leafs_to_bitmap_map_chunks)