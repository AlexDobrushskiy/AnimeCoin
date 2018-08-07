import os
import random
import uuid
import asyncio
import zmq
import zmq.asyncio

from datetime import datetime as dt

from masternode_modules.chunk_manager import ChunkManager
from masternode_modules.settings import MasterNodeSettings
from masternode_modules.helpers import generate_chunks, generate_masternodes, int_to_hex

BASEDIR = "/home/synapse/tmp/animecoin/tmpstorage"


async def heartbeat():
    while True:
        print("HB", dt.now())
        await asyncio.sleep(1)


async def send_rpc_to_random_mn(masternode_list, myid):
    SLEEPTIME = 1
    ctx = zmq.asyncio.Context()
    sockets = {}
    while True:
        nodeid, ip, port, pubkey = random.choice(masternode_list)
        print("%s Sending request to MN: %s" % (myid, nodeid))

        if sockets.get(nodeid) is None:
            sock = ctx.socket(zmq.DEALER)
            sock.setsockopt(zmq.IDENTITY, bytes(str(uuid.uuid4()), "utf-8"))
            sock.connect("tcp://%s:%s" % (ip, port))
            sockets[nodeid] = sock

        sock = sockets[nodeid]
        start = dt.now()
        await sock.send_multipart([b'PING'])

        print("%s Sent request to MN: %s, waiting for reply" % (myid, nodeid))
        msg = await sock.recv_multipart()  # waits for msg to be ready
        stop = dt.now()
        elapsed = (stop-start).total_seconds()

        print("%s Received reply: %s from %s in %ss, sleeping for %ss" % (myid, msg, nodeid, elapsed, SLEEPTIME))
        await asyncio.sleep(SLEEPTIME)

if __name__ == "__main__":
    NUM_CHUNKS = 100
    CHUNK_SIZE = 128
    NUM_MN = 3

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

    # start async loops
    loop = asyncio.get_event_loop()
    for mn in masternodes:
        loop.create_task(mn.zmq_run_forever())

    # loop.create_task(heartbeat())

    for i in range(5):
        loop.create_task(send_rpc_to_random_mn(masternode_list, i))

    loop.run_forever()

    # input("Waiting for keypress: ")
    # for mn in masternodes:
    #     mn.update_mn_list(masternode_list[1:])
    #
    # input("Waiting for keypress: ")
    # newchunk = "42ad07fac0678fa2bac61b0255646ec960dee1bf2b646c88c07fb791c365d3a3"
    # for mn in masternodes:
    #     mn.new_chunks_added_to_blockchain([newchunk])
    #
    # for mn in masternodes:
    #     owner = mn.get_chunk_ownership("42ad07fac0678fa2bac61b0255646ec960dee1bf2b646c88c07fb791c365d3a3")
    #     print("MN %s, owner: %s" % (mn, owner))
