from bitcoinrpc.authproxy import AuthServiceProxy

from core_modules.blackbox_modules.blockchain import store_data_in_utxo,\
    retrieve_data_from_utxo
from core_modules.settings import NetWorkSettings


class BlockChain:
    def __init__(self, user, password, ip, rpcport):
        url = "http://%s:%s@%s:%s" % (user, password, ip, rpcport)
        self.jsonrpc = AuthServiceProxy(url)

    def bootstrap(self, addr):
        return self.jsonrpc.addnode(addr, "onetry")

    def search_chain(self):
        blockcount = int(self.jsonrpc.getblockcount()) - 1
        for blocknum in range(1, blockcount + 1):
            block = self.jsonrpc.getblock(str(blocknum))
            if block["confirmations"] < NetWorkSettings.REQUIRED_CONFIRMATIONS:
                break

            for txid in block["tx"]:
                yield txid

    def store_data_in_utxo(self, input_data):
        return store_data_in_utxo(self.jsonrpc, input_data)

    def retrieve_data_from_utxo(self, blockchain_transaction_id):
        return retrieve_data_from_utxo(self.jsonrpc, blockchain_transaction_id)
