import time
import unittest

import bitcoinrpc


from core_modules.blockchain import BlockChain
from test.helpers import Daemon


class TestBlockChain(unittest.TestCase):
    def setUp(self):
        self.daemon = Daemon("rt", "rt", 10001, "127.0.0.1", 10002)
        self.daemon.start()

        # connect to daemon
        while True:
            blockchain = BlockChain(user=self.daemon.rpcuser,
                                    password=self.daemon.rpcpassword,
                                    ip=self.daemon.ip,
                                    rpcport=self.daemon.rpcport)
            try:
                blockchain.jsonrpc.getwalletinfo()
            except (ConnectionRefusedError, bitcoinrpc.authproxy.JSONRPCException) as exc:
                print("Exception %s while getting wallet info, retrying..." % exc)
                time.sleep(0.5)
            else:
                break

        self.blockchain = blockchain

        # generate some coins
        self.blockchain.jsonrpc.generate(100)
        self.blockchain.jsonrpc.generate(100)

    def tearDown(self):
        self.daemon.stop()

    def test_blockchain_storage(self):
        origdata = b'THIS IS SOME TEST DATA'
        txid = self.blockchain.store_data_in_utxo(origdata)
        retdata = self.blockchain.retrieve_data_from_utxo(txid)
        self.assertEquals(origdata, retdata)
