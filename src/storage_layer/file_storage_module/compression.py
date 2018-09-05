import hashlib
import tarfile

import zstandard as zstd


def compress_data_with_zstd_func(input_data, zstd_compression_level):
    zstandard_compressor = zstd.ZstdCompressor(level=zstd_compression_level)
    zstd_compressed_data = zstandard_compressor.compress(input_data)
    return zstd_compressed_data


def decompress_data_with_zstd_func(zstd_compressed_data):
    zstandard_decompressor = zstd.ZstdDecompressor()
    uncompressed_data = zstandard_decompressor.decompress(zstd_compressed_data)
    return uncompressed_data
