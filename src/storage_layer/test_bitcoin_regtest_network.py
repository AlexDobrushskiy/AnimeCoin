import sys
import os
import shutil

from dht_prototype.masternode_daemon import MasterNode


def test_store_and_retrieve_data(nodes):
    testdata = b'THIS IS TEST DATA'

    # nodes[0].chainwrapper.generate(100)
    txid = nodes[0].chainwrapper.store_ticket(testdata)

    # mine a block
    nodes[0].chainwrapper.generate(1)

    resp = nodes[1].chainwrapper.retrieve_ticket(txid)
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


if __name__ == "__main__":
    basedir = sys.argv[1]
    daemon_binary = sys.argv[2]
    example_config = sys.argv[3]

    # TODO: clean up and prepare basedirs
    #  o create folder structure
    #  o place default animecoin.conf

    masternodes = []
    for i in range(0, 1):
        node_dir = os.path.join(basedir, "node%s" % i)
        prepare_node_directory(node_dir, example_config)

        mn = MasterNode(node_dir, daemon_binary)
        masternodes.append(mn)

    for node in masternodes:
        node.start_bitcoind()

    mn = masternodes[0]
    print("BEST BLOCK HASH", mn.chainwrapper.getbestblockhash())
    for ticket in mn.chainwrapper.all_ticket_iterator():
        print("TICKET", ticket)

    # test_store_and_retrieve_data(masternodes)
    # ChainWrapper

    input("Press enter to stop daemon: ")

    for node in masternodes:
        node.stop_bitcoind()
