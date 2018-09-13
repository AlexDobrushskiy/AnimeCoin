import asyncio
import sys
import os

from datetime import datetime as dt, timedelta as td

from dht_prototype.masternode_daemon import MasterNodeDaemon
from dht_prototype.masternode_modules.masternode_discovery import discover_nodes


async def heartbeat():
    while True:
        print("HB", dt.now())
        await asyncio.sleep(1)


def test_store_and_retrieve_data(srcnode, dstnode):
    testdata = b'THIS IS TEST DATA'

    # nodes[0].chainwrapper.generate(100)
    txid = srcnode.chainwrapper.store_ticket(testdata)

    # mine a block
    # srcnode.chainwrapper.generate(1)

    resp = dstnode.chainwrapper.retrieve_ticket(txid)
    assert(testdata == resp)


def start_masternodes(settings_list):
    masternodes = {}
    for settings in settings_list:
        os.makedirs(settings["basedir"], exist_ok=True)
        os.makedirs(os.path.join(settings["basedir"], "config"), exist_ok=True)

        mn = MasterNodeDaemon(settings=settings)

        nodename = settings["nodename"]
        masternodes[nodename] = mn
        print("Found masternode %s!" % nodename)

        # if len(masternodes) > 1:
        #     print("ABORTING EARLY")
        #     break

    return masternodes


if __name__ == "__main__":
    path_to_daemon_binary = sys.argv[1]
    regtestdir = sys.argv[2]

    settings_list = discover_nodes(path_to_daemon_binary, regtestdir)
    masternodes = start_masternodes(settings_list)

    for nodeid, mn in masternodes.items():
        for othernodeid, othermn in masternodes.items():
            mn_info = othermn.get_masternode_details()
            print("MN INFO", mn_info)
            mn.logic.add_masternode(*mn_info)
            print("Registering MN %s with %s" % (othernodeid, nodeid))

    # srcmn = masternodes["node12"]
    # dstmn = masternodes["node0"]
    # test_store_and_retrieve_data(srcmn, dstmn)

    mn = masternodes["node0"]
    print("Maternode list", mn.blockchain.jsonrpc.masternode("list", "addr"))

    # for ticket in mn.chainwrapper.all_ticket_iterator():
    #     print("TICKET", ticket)

    # test_store_and_retrieve_data(masternodes)
    # ChainWrapper

    # start async loops
    loop = asyncio.get_event_loop()

    loop.create_task(heartbeat())

    for nodeid, mn in masternodes.items():
        loop.create_task(mn.logic.zmq_run_forever())
        # loop.create_task(mn.logic.run_heartbeat_forever())
        # loop.create_task(mn.logic.issue_random_tests_forever(1))
        loop.create_task(mn.logic.run_workers_forever())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Stopping masternodes")
    finally:
        for nodeid, mn in masternodes.items():
            print("Stopping MN %s" % nodeid)
            mn.stop_cmn()
