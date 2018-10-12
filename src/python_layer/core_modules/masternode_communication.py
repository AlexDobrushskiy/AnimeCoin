import random


from core_modules.zmq_rpc import RPCClient
from core_modules.helpers import get_nodeid_from_pubkey
from core_modules.masternode_discovery import discover_nodes
from core_modules.settings import NetWorkSettings
from core_modules.logger import initlogging


class NodeManager:
    def __init__(self, nodenum, privkey, pubkey):
        self.__masternodes = {}
        self.__nodenum = nodenum
        self.__logger = initlogging(nodenum, __name__)
        self.__privkey = privkey
        self.__pubkey = pubkey

    def get(self, nodeid):
        return self.__masternodes[nodeid]

    def get_all(self):
        return tuple(self.__masternodes.values())

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

    def get_masternode_ordering(self, blocknum):
        if NetWorkSettings.VALIDATE_MN_SIGNATURES:
            # TODO: We need to return rpcclient instances for each MN
            raise NotImplementedError("TODO")
        else:
            mnlist = self.get_all()[1:4]
            return mnlist

    def update_masternode_list(self):
        # TODO: this list should come from cNode
        if not NetWorkSettings.DEBUG:
            raise NotImplementedError()

        # parse new list
        new_mn_list = {}
        for pubkey, ip, pyrpcport in NetWorkSettings.MASTERNODE_LIST:
            nodeid = get_nodeid_from_pubkey(pubkey)
            new_mn_list[nodeid] = RPCClient(self.__nodenum, self.__privkey, self.__pubkey,
                                            nodeid, ip, pyrpcport, pubkey)

        old = set(self.__masternodes.keys())
        new = set(new_mn_list.keys())
        added = new - old
        removed = old - new

        for i in added:
            self.__logger.debug("Added MN %s" % i)
        for i in removed:
            self.__logger.debug("Removed MN %s" % i)

        self.__masternodes = new_mn_list
        return added, removed
