import random
import os
import sys

from dht_prototype.masternode_modules.blockchain import BlockChain

# bitcoind cmdline:
#   bitcoind -rpcuser=test -rpcpassword=testpw -regtest -server -addresstype=legacy
# mine coins:
#   bitcoin-cli -rpcuser=test -rpcpassword=testpw -regtest generate 100

MAINNET_BTC = "18443"
MAINNET_ANIME = "19932"
PORT = MAINNET_BTC


def test(blockchain, original):
    # print("ORIGINAL DATA LENGTH:", len(original))
    # print("ORIGINAL DATA", original)
    transid = blockchain.store_data_in_utxo(original)
    reconstructed = blockchain.retrieve_data_from_utxo(transid)
    # print("RECONSTRUCTED", reconstructed)
    assert(original == reconstructed)


def main():
    blockchain = BlockChain("test", "testpw", "127.0.0.1", PORT)
    # print(blockchain.getbestblockhash())

    # print(blockchain.listtransactions())

    # filename = sys.argv[1]
    # original = open(filename, "rb").read()
    # test(blockchain, original)

    for datalen in range(0, 100):
        # datalen = random.randint(0, 100)
        killerdata = os.urandom(random.randint(0, 10))
        print("len: %s, killerdata: %s" % (datalen, killerdata))
        original = b'X' * datalen + killerdata
        try:
            test(blockchain, original)
        except Exception as exc:
            print("FOUND EXCEPTION %s for input: %s" % (exc, original))
            raise


if __name__ == "__main__":
    main()
