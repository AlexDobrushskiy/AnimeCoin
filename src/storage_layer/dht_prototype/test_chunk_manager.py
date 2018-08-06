import os

from masternode_modules.chunk_manager import ChunkManager
from masternode_modules.settings import MasterNodeSettings
from masternode_modules.helpers import generate_chunks, generate_masternodes, int_to_hex

BASEDIR = "/home/synapse/tmp/animecoin/tmpstorage"


if __name__ == "__main__":
    NUM_CHUNKS = 1000
    CHUNK_SIZE = 128
    NUM_MN = 10

    masternode_list = generate_masternodes(NUM_MN, "127.0.0.1", 86752, None)

    chunks = [int_to_hex(x) for x in generate_chunks(NUM_CHUNKS, CHUNK_SIZE).keys()]

    masternodes = []
    for i, config in enumerate(masternode_list):
        name = "mn_%s" % i
        chunkdir = os.path.join(BASEDIR, name)
        os.makedirs(chunkdir, exist_ok=True)
        masternode_settings = MasterNodeSettings(basedir=chunkdir)

        nodeid, ip, port, pubkey = config
        mn = ChunkManager(name, nodeid, masternode_settings, chunks, masternode_list)
        masternodes.append(mn)

    input("Waiting for keypress: ")
    for mn in masternodes:
        mn.update_mn_list(masternode_list[1:])

    input("Waiting for keypress: ")
    newchunk = "42ad07fac0678fa2bac61b0255646ec960dee1bf2b646c88c07fb791c365d3a3"
    for mn in masternodes:
        mn.new_chunks_added_to_blockchain([newchunk])

    for mn in masternodes:
        owner = mn.get_chunk_ownership("42ad07fac0678fa2bac61b0255646ec960dee1bf2b646c88c07fb791c365d3a3")
        print("MN %s, owner: %s" % (mn, owner))
