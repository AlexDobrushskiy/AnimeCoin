import sys
import os
import subprocess
import time
import http

from dht_prototype.masternode_modules.blockchain import BlockChain
from dht_prototype.masternode_modules.blockchain_wrapper import MockChain, ChainWrapper


BITCOIN_BOOT_WAIT_TIME = 0.5    # time to wait until bitcoind comes up


class BitcoinNode:
    def __init__(self, nodeid, port, rpcport, datadir, bootstrapport):
        self.nodeid = nodeid
        self.port = port
        self.rpcport = rpcport
        self.datadir = datadir
        self.bootstrapport = bootstrapport

        self.process = None
        self.blockchain = None

    def start(self):
        if self.process is None:
            print("Starting node", self.nodeid)
            self.process = subprocess.Popen(["bitcoind", "-rpcuser=test", "-rpcpassword=testpw", "-regtest", "-txindex",
                                             "-rpcport=%s" % self.rpcport, "-port=%s" % self.port, "-server",
                                             "-addresstype=legacy", "-discover=0", "-datadir=%s" % self.datadir])

            # connect to daemon
            self.blockchain = BlockChain("test", "testpw", "127.0.0.1", self.rpcport)
            time.sleep(BITCOIN_BOOT_WAIT_TIME)
            self.blockchain.getwalletinfo()

            if self.bootstrapport is not None:
                print("Connecting to %s" % self.bootstrapport)
                self.blockchain.bootstrap("127.0.0.1:%s" % self.bootstrapport)

    def stop(self):
        if self.process is not None:
            print("Stopping node", self.nodeid)
            self.process.terminate()
            self.process.wait()


if __name__ == "__main__":
    basedir = sys.argv[1]

    nodes = [
        BitcoinNode(nodeid="#1", port=12340, rpcport=10340, datadir=os.path.join(basedir, "node1"), bootstrapport=None),
        BitcoinNode(nodeid="#2", port=12341, rpcport=10341, datadir=os.path.join(basedir, "node2"), bootstrapport=12340),
        BitcoinNode(nodeid="#3", port=12342, rpcport=10342, datadir=os.path.join(basedir, "node3"), bootstrapport=12341),
    ]

    for node in nodes:
        node.start()

    print("GETINFO:", nodes[0].blockchain.getwalletinfo())
    print("GENERATING COINS:", nodes[0].blockchain.generate(100))
    print("LIST UNSPENT:", nodes[0].blockchain.listunspent())

    testdata = b'THIS IS SOME TEST DATA'
    txid = nodes[0].blockchain.store_data_in_utxo(testdata)

    # mine a block
    nodes[0].blockchain.generate(1)

    try:
        resp = nodes[1].blockchain.retrieve_data_from_utxo(txid)
        print("GOT DATA", testdata, resp)
    finally:
        input("press enter to stop nodes: ")
        for node in nodes:
            node.stop()
