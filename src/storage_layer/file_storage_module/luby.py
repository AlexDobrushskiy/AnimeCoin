import time
import hashlib
import io
import struct
import random
import glob
import os
import math

from struct import pack, unpack
from fs.copy import copy_fs
from fs.memoryfs import MemoryFS
from fs.osfs import OSFS
from collections import defaultdict

from file_storage_module.helpers import PRNG, get_sha256_hash_of_input_data_func
from file_storage_module.compression import add_art_image_files_and_metadata_to_zstd_compressed_tar_file_func


# LT Coding Helper fucntions:
class PRNG(object):
    """
    A Pseudorandom Number Generator that yields samples from the set of source
    blocks using the RSD degree distribution described above.
    """

    def __init__(self, params):
        """Provide RSD parameters on construction """
        self.state = None  # Seed is set by interfacing code using set_seed
        K, delta, c = params
        self.K = K
        self.cdf = self.__gen_rsd_cdf(K, delta, c)

    def __gen_tau(self, S, K, delta):
        """The Robust part of the RSD, we precompute an array for speed"""
        pivot = int(math.floor(K / S))
        return [S / K * 1 / d for d in range(1, pivot)] \
               + [S / K * math.log(S / delta)] \
               + [0 for d in range(pivot, K)]

    def __gen_rho(self, K):
        """The Ideal Soliton Distribution, we precompute an array for speed"""
        return [1 / K] + [1 / (d * (d - 1)) for d in range(2, K + 1)]

    def __gen_mu(self, K, delta, c):
        """The Robust Soliton Distribution on the degree of transmitted blocks"""
        S = c * math.log(K / delta) * math.sqrt(K)
        tau = self.__gen_tau(S, K, delta)
        rho = self.__gen_rho(K)
        normalizer = sum(rho) + sum(tau)
        return [(rho[d] + tau[d]) / normalizer for d in range(K)]

    def __gen_rsd_cdf(self, K, delta, c):
        """The CDF of the RSD on block degree, precomputed for sampling speed"""
        mu = self.__gen_mu(K, delta, c)
        return [sum(mu[:d + 1]) for d in range(K)]


    def _get_next(self):
        """Executes the next iteration of the PRNG evolution process, and returns the result"""
        PRNG_A = 16807
        PRNG_M = (1 << 31) - 1
        self.state = PRNG_A * self.state % PRNG_M
        return self.state

    def _sample_d(self):
        """Samples degree given the precomputed distributions above and the linear PRNG output """
        PRNG_M = (1 << 31) - 1
        PRNG_MAX_RAND = PRNG_M - 1
        p = self._get_next() / PRNG_MAX_RAND
        for ix, v in enumerate(self.cdf):
            if v > p:
                return ix + 1
        return ix + 1

    def set_seed(self, seed):
        """Reset the state of the PRNG to the given seed"""
        self.state = seed

    def get_src_blocks(self, seed=None):
        """
        Returns the indices of a set of `d` source blocks sampled from indices i = 1, ..., K-1 uniformly,
        where `d` is sampled from the RSD described above.
        """
        if seed:
            self.state = seed
        blockseed = self.state
        d = self._sample_d()
        have = 0
        nums = set()
        while have < d:
            num = self._get_next() % self.K
            if num not in nums:
                nums.add(num)
                have += 1
        return blockseed, d, nums


class CheckNode(object):
    def __init__(self, src_nodes, check):
        self.check = check
        self.src_nodes = src_nodes


class BlockGraph(object):
    """Graph on which we run Belief Propagation to resolve source node data"""

    def __init__(self, num_blocks):
        self.checks = defaultdict(list)
        self.num_blocks = num_blocks
        self.eliminated = {}

    def add_block(self, nodes, data):
        """
        Adds a new check node and edges between that node and all source nodes it connects,
        resolving all message passes that become possible as a result.
        """
        if len(nodes) == 1:  # We can eliminate this source node
            to_eliminate = list(self.eliminate(next(iter(nodes)), data))
            while len(to_eliminate):  # Recursively eliminate all nodes that can now be resolved
                other, check = to_eliminate.pop()
                to_eliminate.extend(self.eliminate(other, check))
        else:
            for node in list(nodes):  # Pass messages from already-resolved source nodes
                if node in self.eliminated:
                    nodes.remove(node)
                    data ^= self.eliminated[node]
            if len(nodes) == 1:  # Resolve if we are left with a single non-resolved source node
                return self.add_block(nodes, data)
            else:  # Add edges for all remaining nodes to this check
                check = CheckNode(nodes, data)
                for node in nodes:
                    self.checks[node].append(check)
        return len(self.eliminated) >= self.num_blocks  # Are we done yet?

    def eliminate(self, node, data):
        """Resolves a source node, passing the message to all associated checks """
        self.eliminated[node] = data  # Cache resolved value
        others = self.checks[node]
        del self.checks[node]
        for check in others:  # Pass messages to all associated checks
            check.check ^= data
            check.src_nodes.remove(node)
            if len(check.src_nodes) == 1:  # Yield all nodes that can now be resolved
                yield (next(iter(check.src_nodes)), check.check)


def encode_file_into_luby_blocks_func(block_redundancy_factor, desired_block_size_in_bytes, folder_containing_art_image_and_metadata_files,
                                      path_to_folder_containing_luby_blocks):
    file_paths_in_folder = glob.glob(folder_containing_art_image_and_metadata_files + '*')
    for current_file_path in file_paths_in_folder:
        if current_file_path.split('.')[-1] in ['zst', 'tar']:
            try:
                os.remove(current_file_path)
            except Exception as e:
                print('Error: ' + str(e))
    c_constant = 0.1  # Don't touch
    delta_constant = 0.5  # Don't touch
    start_time = time.time()
    ramdisk_object = MemoryFS()
    c_constant = 0.1
    delta_constant = 0.5
    seed = random.randint(0, 1 << 31 - 1)
    compressed_output_file_path, compressed_file_hash = add_art_image_files_and_metadata_to_zstd_compressed_tar_file_func(
        folder_containing_art_image_and_metadata_files)
    final_art_file__original_size_in_bytes = os.path.getsize(compressed_output_file_path)
    output_blocks_list = []  # Process compressed file into a stream of encoded blocks, and save those blocks as separate files in the output folder:
    print('Now encoding file ' + compressed_output_file_path + ' (' + str(
        round(final_art_file__original_size_in_bytes / 1000000)) + 'mb)\n\n')
    total_number_of_blocks_to_generate = math.ceil(
        (1.00 * block_redundancy_factor * final_art_file__original_size_in_bytes) / desired_block_size_in_bytes)
    print(
        'Total number of blocks to generate for target level of redundancy: ' + str(total_number_of_blocks_to_generate))
    with open(compressed_output_file_path, 'rb') as f:
        compressed_data = f.read()
    compressed_data_size_in_bytes = len(compressed_data)
    blocks = [
        int.from_bytes(compressed_data[ii:ii + desired_block_size_in_bytes].ljust(desired_block_size_in_bytes, b'0'),
                       'little') for ii in range(0, compressed_data_size_in_bytes, desired_block_size_in_bytes)]
    prng = PRNG(params=(len(blocks), delta_constant, c_constant))
    prng.set_seed(seed)
    output_blocks_list = list()
    number_of_blocks_generated = 0
    while number_of_blocks_generated < total_number_of_blocks_to_generate:
        random_seed, d, ix_samples = prng.get_src_blocks()
        block_data = 0
        for ix in ix_samples:
            block_data ^= blocks[ix]
        block_data_bytes = int.to_bytes(block_data, desired_block_size_in_bytes, 'little')
        block_data_hash = hashlib.sha3_256(block_data_bytes).digest()
        block = (
        compressed_data_size_in_bytes, desired_block_size_in_bytes, random_seed, block_data_hash, block_data_bytes)
        header_bit_packing_pattern_string = '<3I32s'
        bit_packing_pattern_string = header_bit_packing_pattern_string + str(desired_block_size_in_bytes) + 's'
        length_of_header_in_bytes = struct.calcsize(header_bit_packing_pattern_string)
        packed_block_data = pack(bit_packing_pattern_string, *block)
        if number_of_blocks_generated == 0:  # Test that the bit-packing is working correctly:
            with io.BufferedReader(io.BytesIO(packed_block_data)) as f:
                header_data = f.read(length_of_header_in_bytes)
                # first_generated_block_raw_data = f.read(desired_block_size_in_bytes)
            compressed_input_data_size_in_bytes_test, desired_block_size_in_bytes_test, random_seed_test, block_data_hash_test = unpack(
                header_bit_packing_pattern_string, header_data)
            if block_data_hash_test != block_data_hash:
                print('Error! Block data hash does not match the hash reported in the block header!')
        output_blocks_list.append(packed_block_data)
        number_of_blocks_generated = number_of_blocks_generated + 1
        hash_of_block = get_sha256_hash_of_input_data_func(packed_block_data)
        output_block_file_path = 'FileHash__' + compressed_file_hash + '__Block__' + '{0:09}'.format(
            number_of_blocks_generated) + '__BlockHash_' + hash_of_block + '.block'
        try:
            with ramdisk_object.open(output_block_file_path, 'wb') as f:
                f.write(packed_block_data)
        except Exception as e:
            print('Error: ' + str(e))
    duration_in_seconds = round(time.time() - start_time, 1)
    print('\n\nFinished processing in ' + str(
        duration_in_seconds) + ' seconds! \nOriginal zip file was encoded into ' + str(
        number_of_blocks_generated) + ' blocks of ' + str(
        math.ceil(desired_block_size_in_bytes / 1000)) + ' kilobytes each. Total size of all blocks is ~' + str(
        math.ceil((number_of_blocks_generated * desired_block_size_in_bytes) / 1000000)) + ' megabytes\n')
    print('Now copying encoded files from ram disk to local storage...')
    block_storage_folder_path = path_to_folder_containing_luby_blocks
    if not os.path.isdir(block_storage_folder_path):
        os.makedirs(block_storage_folder_path)
    filesystem_object = OSFS(block_storage_folder_path)
    copy_fs(ramdisk_object, filesystem_object)
    print('Done!\n')
    ramdisk_object.close()
    return duration_in_seconds


def reconstruct_data_from_luby_blocks(path_to_folder_containing_luby_blocks):
    c_constant = 0.1
    delta_constant = 0.5
    list_of_luby_block_file_paths = glob.glob(path_to_folder_containing_luby_blocks + '*.block')
    list_of_luby_block_data_binaries = list()
    for current_luby_block_file_path in list_of_luby_block_file_paths:
        try:
            with open(current_luby_block_file_path, 'rb') as f:
                current_luby_block_binary_data = f.read()
            list_of_luby_block_data_binaries.append(current_luby_block_binary_data)
        except Exception as e:
            print('Error: ' + str(e))
    header_bit_packing_pattern_string = '<3I32s'
    length_of_header_in_bytes = struct.calcsize(header_bit_packing_pattern_string)
    first_block_data = list_of_luby_block_data_binaries[0]
    with io.BytesIO(first_block_data) as f:
        compressed_input_data_size_in_bytes, desired_block_size_in_bytes, _, _ = unpack(
            header_bit_packing_pattern_string, f.read(length_of_header_in_bytes))
    minimum_number_of_blocks_required = math.ceil(compressed_input_data_size_in_bytes / desired_block_size_in_bytes)
    block_graph = BlockGraph(minimum_number_of_blocks_required)
    number_of_lt_blocks_found = len(list_of_luby_block_data_binaries)
    print('Found ' + str(number_of_lt_blocks_found) + ' LT blocks to use...')
    for block_count, current_packed_block_data in enumerate(list_of_luby_block_data_binaries):
        with io.BytesIO(current_packed_block_data) as f:
            header_data = f.read(length_of_header_in_bytes)
            compressed_input_data_size_in_bytes, desired_block_size_in_bytes, random_seed, reported_block_data_hash = unpack(
                header_bit_packing_pattern_string, header_data)
            block_data_bytes = f.read(desired_block_size_in_bytes)
            calculated_block_data_hash = hashlib.sha3_256(block_data_bytes).digest()
            if calculated_block_data_hash == reported_block_data_hash:
                if block_count == 0:
                    print('Calculated block data hash matches the reported blocks from the block header!')
                prng = PRNG(params=(minimum_number_of_blocks_required, delta_constant, c_constant))
                _, _, src_blocks = prng.get_src_blocks(seed=random_seed)
                block_data_bytes_decoded = int.from_bytes(block_data_bytes, 'little')
                file_reconstruction_complete = block_graph.add_block(src_blocks, block_data_bytes_decoded)
                if file_reconstruction_complete:
                    break
            else:
                print(
                    'Block data hash does not match reported block hash from block header file! Skipping to next block...')

    if file_reconstruction_complete:
        print('\nDone reconstructing data from blocks! Processed a total of ' + str(block_count + 1) + ' blocks\n')
        incomplete_file = 0
    else:
        print('Warning! Processed all available LT blocks but still do not have the entire file!')
        incomplete_file = 1
    if not incomplete_file:
        with io.BytesIO() as f:
            for ix, block_bytes in enumerate(map(lambda p: int.to_bytes(p[1], desired_block_size_in_bytes, 'little'),
                                                 sorted(block_graph.eliminated.items(), key=lambda p: p[0]))):
                if (ix < minimum_number_of_blocks_required - 1) or (
                                (compressed_input_data_size_in_bytes % desired_block_size_in_bytes) == 0):
                    f.write(block_bytes)
                else:
                    f.write(block_bytes[:compressed_input_data_size_in_bytes % desired_block_size_in_bytes])
                reconstructed_data = f.getvalue()
    if not incomplete_file and type(reconstructed_data) in [bytes, bytearray]:
        print('Successfully reconstructed file from LT blocks! Reconstucted file size is ' + str(
            len(reconstructed_data)) + ' bytes.')
        return reconstructed_data
    else:
        print('\nError: Data reconstruction from LT blocks failed!\n\n')
