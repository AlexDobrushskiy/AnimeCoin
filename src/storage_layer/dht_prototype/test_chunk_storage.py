import hashlib
import random

from masternode_modules.chunk_storage import ChunkStorage


def getrandbytes(n):
    return random.getrandbits(n * 8).to_bytes(n, byteorder="big")


def get_digest(data):
    sha256 = hashlib.sha256()
    sha256.update(data)
    return sha256.hexdigest()


if __name__ == "__main__":
    BASEDIR = "/home/synapse/tmp/animecoin/tmpstorage/"
    x = ChunkStorage(BASEDIR, mode=0o0755)

    chunks = {}
    for i in range(1000):
        data = getrandbytes(1024*1024)
        data_digest = get_digest(data)
        data_key = data_digest
        chunks[data_key] = data

    for chunkname, data in chunks.items():
        x.put(chunkname, data)

    for chunkname in random.sample(chunks.keys(), 100):
        data = x.get(chunkname)
        verification_digest = get_digest(data)
        if verification_digest != chunkname:
            print("Verification mismatch!", chunkname)
        else:
            print("Chunk verified %s: %s" % (chunkname, len(data)))
