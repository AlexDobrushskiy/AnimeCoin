import random


from .zmq_rpc import RPCClient
from .helpers import get_hexdigest, hex_to_int, int_to_hex


class NodeManager:
    def __init__(self, logger, privkey, pubkey):
        self.__masternodes = {}
        self.__logger = logger
        self.__privkey = privkey
        self.__pubkey = pubkey

    def add_masternode(self, nodeid, ip, port, pubkey, keytype):
        if keytype == "file":
            pubkey = open(pubkey).read()
        self.__masternodes[nodeid] = RPCClient(self.__logger, self.__privkey, self.__pubkey, nodeid, ip, port, pubkey)

    def get(self, nodeid):
        return self.__masternodes[nodeid]

    def get_all(self):
        return list(self.__masternodes.values())

    def get_random(self):
        try:
            sample = random.sample(self.get_all(), 1)
        except ValueError:
            return None
        return sample[0]

    def get_other_nodes(self, mynodeid):
        other_nodes = []
        for mn in self.__masternodes.values():
            if mn.nodeid != mynodeid:
                other_nodes.append(mn.nodeid)
        return other_nodes

    def update_maternode_list(self, masternode_list):
        # parse new list
        new_mn_list = {}
        for nodeid, ip, port, privkey, pubkey in masternode_list:
            nodeid = hex_to_int(nodeid)
            new_mn_list[nodeid] = RPCClient(self.__logger, self.__privkey, self.__pubkey, nodeid, ip, port, pubkey)

        old = set(self.__masternodes.keys())
        new = set(new_mn_list.keys())
        added = new-old
        removed = old-new
        self.__masternodes = new_mn_list
        return added, removed
