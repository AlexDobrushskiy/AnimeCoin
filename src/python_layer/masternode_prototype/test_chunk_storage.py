import sys

from core_modules.chunk_storage import ChunkStorage
from core_modules.helpers import get_intdigest, generate_chunks


if __name__ == "__main__":
    basedir = sys.argv[1]
    NUM_CHUNKS = 100
    CHUNK_SIZE = 1024*1024

    x = ChunkStorage(basedir + "/chunkdata", mode=0o0700)

    print("[+] Generating %s chunks of size %s" % (NUM_CHUNKS, CHUNK_SIZE))
    chunks = generate_chunks(NUM_CHUNKS, CHUNK_SIZE)

    print("[+] Storing chunks")
    for chunkname, data in chunks.items():
        x.put(chunkname, data)

    print("[+] Verifying chunks")
    for chunkname in chunks.keys():
        data = x.get(chunkname)
        verification_digest = get_intdigest(data)
        if verification_digest != chunkname:
            print("Verification mismatch!", chunkname)

    input("Corrupt a chunk")
    print("[+] Indexing and verifying chunks")
    for chunk in x.index():
        if not x.verify(chunk):
            print("Verify failed for chunk %s" % (chunk))

    print("[+] Deleting chunks")
    for chunkname in chunks:
        x.exists(chunkname)
