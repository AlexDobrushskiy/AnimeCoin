import sys
import os
import shutil

from dht_prototype.masternode_daemon import MasterNode


def test_store_and_retrieve_data(srcnode, dstnode):
    testdata = b'THIS IS TEST DATA'

    # nodes[0].chainwrapper.generate(100)
    txid = srcnode.chainwrapper.store_ticket(testdata)

    # mine a block
    # srcnode.chainwrapper.generate(1)

    resp = dstnode.chainwrapper.retrieve_ticket(txid)
    assert(testdata == resp)


def prepare_node_directory(node_dir, example_config):
    blockchaindir = os.path.join(node_dir, "blockchain")

    print("Creating blockchain directory")
    os.makedirs(blockchaindir, exist_ok=True)

    print("Copying over example config file")
    try:
        open(os.path.join(blockchaindir, "animecoin.conf"))
    except FileNotFoundError:
        shutil.copy(example_config, blockchaindir)


def parse_regtest_dir(regtestdir):
    masternodes = {}
    for dir in sorted(os.listdir(regtestdir)):
        settingsfile = os.path.join(regtestdir, dir, "animecoin.conf")

        settings = {}
        for line in open(settingsfile):
            line = line.strip().split("=")
            settings[line[0]] = line[1]

        # set our settings
        settings["chunkdir"] = os.path.join(regtestdir, dir, "pymn", "chunks")
        os.makedirs(settings["chunkdir"], exist_ok=True)

        nodeid = dir.lstrip("node")
        print("NODEID", nodeid)
        mn = MasterNode(nodeid=dir, settings=settings)
        masternodes[dir] = mn
        print("Found masternode %s!" % dir)
    return masternodes


if __name__ == "__main__":
    regtestdir = sys.argv[1]

    masternodes = parse_regtest_dir(regtestdir)

    # for nodeid, mn in masternodes.items():
    #     print("WALLET INFO", nodeid, mn.blockchain.jsonrpc.getwalletinfo())

    # srcmn = masternodes["node12"]
    # dstmn = masternodes["node0"]
    # test_store_and_retrieve_data(srcmn, dstmn)

    mn = masternodes["node0"]
    print("Maternode list", mn.blockchain.jsonrpc.masternode("list", "addr"))

    # for ticket in mn.chainwrapper.all_ticket_iterator():
    #     print("TICKET", ticket)

    # test_store_and_retrieve_data(masternodes)
    # ChainWrapper
