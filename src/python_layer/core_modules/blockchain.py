from bitcoinrpc.authproxy import AuthServiceProxy

from core_modules.blackbox_modules.blockchain import store_data_in_utxo,\
    retrieve_data_from_utxo
from core_modules.settings import NetWorkSettings

# TODO: type check all these rpc calls, so that we can rely on it better


class BlockChain:
    def __init__(self, user, password, ip, rpcport):
        url = "http://%s:%s@%s:%s" % (user, password, ip, rpcport)
        self.jsonrpc = AuthServiceProxy(url)

    def get_masternode_order(self, blocknum):
        # TODO: should return MN list: [(sha256(pubkey), ip, port, pubkey), (sha256(pubkey), ip, port, pubkey)...]
        # sha256(pubkey) is the nodeid as int
        raise NotImplementedError("TODO")

    def addnode(self, node, mode):
        return self.jsonrpc.addnode(node, mode)

    def listunspent(self, minimum=1, maximum=9999999, addresses=[]):
        return self.jsonrpc.listunspent(minimum, maximum, addresses)

    def getblockchaininfo(self):
        return self.jsonrpc.getblockchaininfo()

    def getbalance(self):
        return self.jsonrpc.getbalance()

    def sendtoaddress(self, address, amount):
        return self.jsonrpc.sendtoaddress(address, amount)

    def getblock(self, blocknum):
        return self.jsonrpc.getblock(blocknum)

    def getblockcount(self):
        return int(self.jsonrpc.getblockcount())

    def getaccountaddress(self, address):
        return self.jsonrpc.getaccountaddress(address)

    def mnsync(self, param):
        return self.jsonrpc.mnsync(param)

    def gettransaction(self, txid):
        return self.jsonrpc.gettransaction(txid)

    def listsinceblock(self):
        return self.jsonrpc.listsinceblock()

    def getbestblockhash(self):
        return self.jsonrpc.getbestblockhash()

    def getwalletinfo(self):
        return self.jsonrpc.getwalletinfo()

    def getrawtransaction(self, txid, verbose):
        return self.jsonrpc.getrawtransaction(txid, verbose)

    def generate(self, n):
        return self.jsonrpc.generate(n)

    def search_chain(self, confirmations=NetWorkSettings.REQUIRED_CONFIRMATIONS):
        blockcount = int(self.jsonrpc.getblockcount()) - 1
        for blocknum in range(1, blockcount + 1):
            block = self.jsonrpc.getblock(str(blocknum))
            if block["confirmations"] < confirmations:
                break

            for txid in block["tx"]:
                yield txid

    def store_data_in_utxo(self, input_data):
        txid = store_data_in_utxo(self.jsonrpc, input_data)
        return txid

    def retrieve_data_from_utxo(self, blockchain_transaction_id):
        return retrieve_data_from_utxo(self.jsonrpc, blockchain_transaction_id)
