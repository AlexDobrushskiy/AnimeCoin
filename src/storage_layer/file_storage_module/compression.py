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


def add_art_image_files_and_metadata_to_zstd_compressed_tar_file_func(folder_containing_art_image_and_metadata_files):
    with tarfile.open(folder_containing_art_image_and_metadata_files + 'art_files.tar', 'w') as tar:
        tar.add(folder_containing_art_image_and_metadata_files, arcname='.')
    with open(folder_containing_art_image_and_metadata_files + 'art_files.tar', 'rb') as f:
        tar_binary_data = f.read()
    tar_file_hash = hashlib.sha3_256(tar_binary_data).hexdigest()
    zstd_compression_level = 15
    print('Now compressing art image and metadata files with Z-Standard...')
    compressed_tar_binary_data = compress_data_with_zstd_func(tar_binary_data, zstd_compression_level)
    print('Done!')
    compressed_output_file_path = folder_containing_art_image_and_metadata_files + 'art_files_compressed.zst'
    with open(compressed_output_file_path, 'wb') as f:
        f.write(compressed_tar_binary_data)
    with open(compressed_output_file_path, 'rb') as f:
        compressed_binary_data_test = f.read()
    compressed_file_hash = hashlib.sha3_256(compressed_binary_data_test).hexdigest()
    decompressed_data = decompress_data_with_zstd_func(compressed_binary_data_test)
    decompressed_file_hash = hashlib.sha3_256(decompressed_data).hexdigest()
    assert (decompressed_file_hash == tar_file_hash)
    return compressed_output_file_path, compressed_file_hash
