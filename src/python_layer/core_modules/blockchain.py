from bitcoinrpc.authproxy import AuthServiceProxy

from core_modules.blackbox_modules.blockchain import store_data_in_utxo,\
    retrieve_data_from_utxo


class BlockChain:
    def __init__(self, user, password, ip, rpcport):
        url = "http://%s:%s@%s:%s" % (user, password, ip, rpcport)
        self.jsonrpc = AuthServiceProxy(url)

    def bootstrap(self, addr):
        return self.jsonrpc.addnode(addr, "onetry")

    def search_chain(self):
        processed = 0
        while True:
            # TODO: handle blocks being added here
            transactions = self.jsonrpc.listtransactions("*", 1000, processed)
            if len(transactions) == 0:
                break
            for transaction in transactions:
                txid = transaction["txid"]

                # print("TRANSACTION", processed, transaction["time"], txid, transaction)
                yield txid
                processed += 1

    def store_data_in_utxo(self, input_data):
        return store_data_in_utxo(self.jsonrpc, input_data)

    def retrieve_data_from_utxo(self, blockchain_transaction_id):
        return retrieve_data_from_utxo(self.jsonrpc, blockchain_transaction_id)
