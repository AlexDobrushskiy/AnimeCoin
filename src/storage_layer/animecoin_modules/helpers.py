import time
import random
import hashlib


class AnimeTimer:
    def __init__(self):
        self.start = time.time()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end = time.time()
        runtime = end - self.start
        msg = '({time} seconds to complete)'
        print(msg.format(time=round(runtime, 5)))


def sleep_rand():
    time.sleep(0.05 * random.random())


def get_sha3_512_func(input_data_or_string):
    if isinstance(input_data_or_string, str):
        input_data_or_string = input_data_or_string.encode('utf-8')
    hash_of_input_data = hashlib.sha3_512(input_data_or_string).hexdigest()
    return hash_of_input_data
