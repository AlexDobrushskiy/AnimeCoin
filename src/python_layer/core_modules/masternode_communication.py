import random


from core_modules.zmq_rpc import RPCClient
from core_modules.helpers import get_intdigest, hex_to_int
from core_modules.masternode_discovery import discover_nodes
from core_modules.settings import NetWorkSettings


class NodeManager:
    def __init__(self, logger, privkey, pubkey, configdir):
        self.__masternodes = {}
        self.__logger = logger
        self.__privkey = privkey
        self.__pubkey = pubkey

        # TODO: remove this
        self.__configdir = configdir
        if self.__configdir is not None:
            self.__update_masternode_list()

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

    def get_masternode_ordering(self, blocknum):
        if NetWorkSettings.VALIDATE_MN_SIGNATURES:
            # TODO: We need to return rpcclient instances for each MN
            raise NotImplementedError("TODO")
        else:
            mnlist = self.get_all()[1:4]
            return mnlist

    def __update_masternode_list(self):
        # TODO: this list should come from cNode
        settings_list = discover_nodes(self.__configdir)

        # parse new list
        new_mn_list = {}
        for settings in settings_list:
            pubkey = open(settings["pubkey"], "rb").read()
            nodeid = get_intdigest(pubkey)
            new_mn_list[nodeid] = RPCClient(self.__logger, self.__privkey, self.__pubkey,
                                            nodeid, settings["ip"], settings["pyrpcport"], pubkey)

        old = set(self.__masternodes.keys())
        new = set(new_mn_list.keys())
        added = new - old
        removed = old - new
        self.__masternodes = new_mn_list
        return added, removed
