import zstd


def compress_data_with_zstd_func(input_data):
    zstd_compression_level = 22  # Highest (best) compression level is 22
    zstandard_compressor = zstd.ZstdCompressor(level=zstd_compression_level)
    if isinstance(input_data, str):
        input_data = input_data.encode('utf-8')
    zstd_compressed_data = zstandard_compressor.compress(input_data)
    return zstd_compressed_data


def decompress_data_with_zstd_func(zstd_compressed_data):
    zstandard_decompressor = zstd.ZstdDecompressor()
    uncompressed_data = zstandard_decompressor.decompress(zstd_compressed_data)
    return uncompressed_data
