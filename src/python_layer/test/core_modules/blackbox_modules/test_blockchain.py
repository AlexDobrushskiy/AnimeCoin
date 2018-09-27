import unittest

from core_modules.blockchain import BlockChain

# bitcoind cmdline:
#   bitcoind -rpcuser=test -rpcpassword=testpw -regtest -server -addresstype=legacy
# mine coins:
#   bitcoin-cli -rpcuser=test -rpcpassword=testpw -regtest generate 100

# TODO: this is an integration test
# TODO: it misses the actual part that starts animecoind


class TestBlockChain(unittest.TestCase):
    @unittest.skip("TODO")
    def test_blockchain_storage(self):
        blockchain = BlockChain("rt", "rt", "127.0.0.1", 10001)
        origdata = b'THIS IS SOME TEST DATA'
        txid = blockchain.store_data_in_utxo(origdata)
        retdata = blockchain.retrieve_data_from_utxo(txid)
        self.assertEquals(origdata, retdata)
