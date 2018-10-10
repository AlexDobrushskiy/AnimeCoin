from core_modules.helpers import get_pynode_digest_int
from core_modules.settings import NetWorkSettings
from core_modules.logger import initlogging


class AliasManager:
    def __init__(self, nodenum, nodeid, mn_manager):
        self.__logger = initlogging(nodenum, __name__)
        self.__nodeid = nodeid
        self.__mn_manager = mn_manager

        # helper lookup table for alias generation and other nodes
        self.__alias_digests = []

        for i in range(NetWorkSettings.REPLICATION_FACTOR):
            digest_int = get_pynode_digest_int(i.to_bytes(1, byteorder='big') + NetWorkSettings.ALIAS_SEED)
            # self.__logger.debug("Alias digest %s -> %s" % (i, chunkid_to_hex(digest_int)))
            self.__alias_digests.append(digest_int)

    def __generate_aliases(self, chunkid):
        for alias_digest in self.__alias_digests:
            yield alias_digest ^ chunkid

    def __we_own_this_alt_key(self, alt_key):
        my_distance = alt_key ^ self.__nodeid

        # check if we are the closest to this chunk
        store = True
        for othernodeid in self.__mn_manager.get_other_nodes(self.__nodeid):
            if alt_key ^ othernodeid < my_distance:
                store = False
                break

        return store

    def calculate_alias_updates(self, chunkid):
        # maintain the alias table
        alias_updates = []
        for alt_key in self.__generate_aliases(chunkid):
            alias_owned = self.__we_own_this_alt_key(alt_key)
            alias_updates.append((alt_key, alias_owned))

        return alias_updates

    def find_owners_for_chunk(self, chunkid):
        owners = set()
        for alt_key in self.__generate_aliases(chunkid):
            # found owner for this alt_key
            owner, min_distance = None, None
            for mn in self.__mn_manager.get_all():
                distance = alt_key ^ mn.nodeid
                if owner is None or distance < min_distance:
                    owner = mn.nodeid
                    min_distance = distance
            owners.add(owner)
        return owners

    def find_other_owners_for_chunk(self, chunkid):
        owners = self.find_owners_for_chunk(chunkid)
        return owners - {self.__nodeid}

    def we_own_chunk(self, chunkid):
        return self.__nodeid in self.find_owners_for_chunk(chunkid)
