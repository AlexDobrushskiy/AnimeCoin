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
    NUM_CHUNKS = 100
    CHUNK_SIZE = 1024*1024

    x = ChunkStorage(BASEDIR, mode=0o0755)

    print("[+] Generating %s chunks of size %s" % (NUM_CHUNKS, CHUNK_SIZE))
    chunks = {}
    for i in range(NUM_CHUNKS):
        data = getrandbytes(CHUNK_SIZE)
        data_digest = get_digest(data)
        data_key = data_digest
        chunks[data_key] = data

    print("[+] Storing chunks")
    for chunkname, data in chunks.items():
        x.put(chunkname, data)

    print("[+] Verifying chunks")
    for chunkname in chunks.keys():
        data = x.get(chunkname)
        verification_digest = get_digest(data)
        if verification_digest != chunkname:
            print("Verification mismatch!", chunkname)

    print("[+] Deleting chunks")
    for chunkname in chunks:
        x.exists(chunkname)
