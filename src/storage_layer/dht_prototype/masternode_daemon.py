from .masternode_modules.database import DummyDatabase as Database
from .masternode_modules.blockchain import DummyBlockChain as BlockChain


class MasterNode:
    def __init__(self, database, blockchain, aiohttpd, mnrpc):
        self.__database = database
        self.__blockchain = blockchain  # xmlrpc pull / zmq push - https://github.com/ANIME-AnimeCoin/AnimeCoin/blob/master/doc/zmq.md
        self.__aiohttpd = aiohttpd      # aiohttpd - https://aiohttp.readthedocs.io/en/stable/
        self.__mnrpc = mnrpc            # aiorpc - https://github.com/choleraehyq/aiorpc


if __name__ == "__main__":
    database = Database()
    blockchain = BlockChain()
    mn = MasterNode(database, blockchain)
