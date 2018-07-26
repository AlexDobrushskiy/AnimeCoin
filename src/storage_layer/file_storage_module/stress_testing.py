import glob
import math
import os
import random


def delete_percentage_of_blocks(path_to_folder_containing_luby_blocks,
                                percentage_of_block_files_to_randomly_delete):
    list_of_block_file_paths = glob.glob(path_to_folder_containing_luby_blocks + '*.block')
    number_of_deleted_blocks = 0
    print('\nNow deleting random block files...')
    for current_file_path in list_of_block_file_paths:
        if random.random() <= percentage_of_block_files_to_randomly_delete:
            try:
                os.remove(current_file_path)
                number_of_deleted_blocks = number_of_deleted_blocks + 1
            except OSError:
                pass
    return number_of_deleted_blocks


def corrupt_percentage_of_blocks(path_to_folder_containing_luby_blocks,
                                 percentage_of_block_files_to_randomly_corrupt,
                                 percentage_of_each_selected_file_to_be_randomly_corrupted):
    list_of_block_file_paths = glob.glob(path_to_folder_containing_luby_blocks + '*.block')
    number_of_corrupted_blocks = 0
    for current_file_path in list_of_block_file_paths:
        if random.random() <= percentage_of_block_files_to_randomly_corrupt:
            number_of_corrupted_blocks = number_of_corrupted_blocks + 1
            total_bytes_of_data_in_chunk = os.path.getsize(current_file_path)
            random_bytes_to_write = 5
            number_of_bytes_to_corrupt = math.ceil(
                total_bytes_of_data_in_chunk * percentage_of_each_selected_file_to_be_randomly_corrupted)
            specific_bytes_to_corrupt = random.sample(range(1, total_bytes_of_data_in_chunk),
                                                      math.ceil(number_of_bytes_to_corrupt / random_bytes_to_write))
            print('Now intentionally corrupting block file: ' + current_file_path.split('\\')[-1])
            with open(current_file_path, 'wb') as f:
                try:
                    for byte_index in specific_bytes_to_corrupt:
                        f.seek(byte_index)
                        f.write(os.urandom(random_bytes_to_write))
                except OSError:
                    pass
    return number_of_corrupted_blocks
