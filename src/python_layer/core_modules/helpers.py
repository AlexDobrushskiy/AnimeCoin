import random

from .settings import NetWorkSettings

CNODE_HASH_ALGO = NetWorkSettings.CNODE_HASH_ALGO
SHA2_HEXFORMAT = "%0" + str(NetWorkSettings.CNODE_HEX_DIGEST_SIZE) + "x"
SHA3_HEXFORMAT = "%0" + str(NetWorkSettings.PYNODE_HEX_DIGEST_SIZE) + "x"


def getrandbytes(n):
    return random.getrandbits(n * 8).to_bytes(n, byteorder="big")


def get_digest(data):
    h = CNODE_HASH_ALGO()
    h.update(data)
    return h.digest()


def get_intdigest(data):
    h = CNODE_HASH_ALGO()
    h.update(data)
    return int.from_bytes(h.digest(), byteorder="big")


def get_hexdigest(data):
    h = CNODE_HASH_ALGO()
    h.update(data)
    return h.hexdigest()


def hex_to_int(digest):
    return int(digest, 16)


def int_to_hex(digest):
    return SHA2_HEXFORMAT % digest


def bytes_from_hex(data):
    return bytes.fromhex(data)


def bytes_to_hex(data):
    return data.hex()


def bytes_to_int(data):
    return int(data.hex(), 16)


def bytes_from_int(data):
    return int.from_bytes(data, byteorder="big")


def require_true(param, msg=""):
    # this function replaces the built in assert function so that we can use this in production when ran with
    # optimizations turned on
    if not param:
        raise AssertionError(msg)


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
