import random

from .settings import NetWorkSettings

HASH_ALGO = NetWorkSettings.HASH_ALGO
HEXFORMAT = "%0" + str(NetWorkSettings.HEX_DIGEST_SIZE) + "x"


def getrandbytes(n):
    return random.getrandbits(n * 8).to_bytes(n, byteorder="big")


def get_digest(data):
    h = HASH_ALGO()
    h.update(data)
    return h.digest()


def get_intdigest(data):
    h = HASH_ALGO()
    h.update(data)
    return int.from_bytes(h.digest(), byteorder="big")


def get_hexdigest(data):
    h = HASH_ALGO()
    h.update(data)
    return h.hexdigest()


def hex_to_int(digest):
    return int(digest, 16)


def int_to_hex(digest):
    return HEXFORMAT % digest


def bytes_from_hex(data):
    return bytes.fromhex(data)


def bytes_to_hex(data):
    return data.hex()


# TEST FUNCTIONS
def generate_chunks(num_chunks, chunk_size):
    chunks = {}
    for i in range(num_chunks):
        data = getrandbytes(chunk_size)
        data_digest = get_intdigest(data)
        data_key = data_digest
        chunks[data_key] = data
    return chunks
# END
