import sys
import random
import os

from dht_prototype.masternode_modules.blockchain import BlockChain

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
    print(blockchain.getbestblockhash())

    filename = sys.argv[1]
    original = open(filename, "rb").read()
    # test(blockchain, original)

    for i in range(100):
        bufsize = random.randint(128, 256)
        # original = b'X' * bufsize
        original = os.urandom(bufsize)
        try:
            test(blockchain, original)
        except Exception:
            print("FOUND EXCEPTION for input: %s" % original)


if __name__ == "__main__":
    main()
