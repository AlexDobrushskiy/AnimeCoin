import random
import os
import sys

from dht_prototype.masternode_modules.blockchain import BlockChain

# bitcoind cmdline:
#   bitcoind -rpcuser=test -rpcpassword=testpw -regtest -server -addresstype=legacy
# mine coins:
#   bitcoin-cli -rpcuser=test -rpcpassword=testpw -regtest generate 100


def test(blockchain, original):
    # print("ORIGINAL DATA LENGTH:", len(original))
    # print("ORIGINAL DATA", original)
    transid = blockchain.store_data_in_utxo(original)
    reconstructed = blockchain.retrieve_data_from_utxo(transid)
    # print("RECONSTRUCTED", reconstructed)
    assert(original == reconstructed)


def main():
    blockchain = BlockChain("rt", "rt", "127.0.0.1", 12253)
    origdata = b'THIS IS SOME TEST DATA'
    txid = blockchain.store_data_in_utxo(origdata)
    retdata = blockchain.retrieve_data_from_utxo(txid)
    assert(origdata == retdata)
    print("Data matches, returned: %s" % retdata)
    exit()

    # fuzzer
    # for datalen in range(0, 100):
    #     # datalen = random.randint(0, 100)
    #     killerdata = os.urandom(random.randint(0, 10))
    #     print("len: %s, killerdata: %s" % (datalen, killerdata))
    #     original = b'X' * datalen + killerdata
    #     try:
    #         test(blockchain, original)
    #     except Exception as exc:
    #         print("FOUND EXCEPTION %s for input: %s" % (exc, original))
    #         raise


if __name__ == "__main__":
    main()
