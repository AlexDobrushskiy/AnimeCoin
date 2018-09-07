import sys
import os

from dht_prototype.masternode_daemon import MasterNode


def test_store_and_retrieve_image(image):
    # nodes[0].chainwrapper.generate(100)
    txid = nodes[0].chainwrapper.store_ticket(testdata)

    # mine a block
    nodes[0].chainwrapper.generate(1)

    resp = nodes[1].chainwrapper.retrieve_ticket(txid)
    assert(testdata == resp)


if __name__ == "__main__":
    basedir = sys.argv[1]

    masternodes = []
    for i in range(0, 2):
        mn = MasterNode(os.path.join(basedir, "node%s" % i))
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
