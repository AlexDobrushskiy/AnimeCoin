import os
import random

from .settings import NetWorkSettings
from .chunk_storage import ChunkStorage
from .helpers import get_digest, get_intdigest, get_hexdigest, hex_to_int, int_to_hex


class Chunk:
    def __init__(self, chunkid, exists=False, verified=False, is_ours=False):
        if type(chunkid) != int:
            raise ValueError("chunkid is not int!")

        self.chunkid = chunkid
        self.exists = exists
        self.verified = verified
        self.is_ours = is_ours

    def __str__(self):
        return "chunkid: %s, exists: %s, verified: %s, is_ours: %s" % (int_to_hex(self.chunkid), self.exists,
                                                                       self.verified, self.is_ours)


class ChunkManager:
    def __init__(self, logger, nodeid, basedir, chunks, mn_manager, todolist):
        # initialize logger
        # IMPORTANT: we must ALWAYS use self.__logger.* for logging and not logging.*,
        # since we need instance-level logging
        self.__logger = logger

        # our node id
        self.__nodeid = nodeid

        # the actual storage layer
        self.__storagedir = os.path.join(basedir, "chunkdata")
        self.__storage = ChunkStorage(self.__storagedir, mode=0o0700)

        # databases we keep
        self.__alias_db = {}
        self.__file_db = {}

        # helper lookup table for alias generation and other nodes
        self.__alias_digests = []

        # table of every chunk we know of
        self.__chunk_table = set((hex_to_int(x) for x in chunks))

        # masternode manager
        self.__mn_manager = mn_manager

        # todolist
        self.__todolist = todolist

        # run other initializations
        self.__initialize()

    def __str__(self):
        return "%s" % self.__nodeid

    def __initialize(self):
        self.__logger.debug("Initializing")

        # sanity check
        self.__mn_manager.get(self.__nodeid)

        # initializations
        self.__init_alias_digests()
        self.__recalculate_ownership_of_all_chunks()
        self.__purge_orphaned_storage_entries()
        self.__purge_orphaned_db_entries()
        self.__purge_orphaned_files()
        self.dump_internal_stats()

    def __init_alias_digests(self):
        for i in range(NetWorkSettings.REPLICATION_FACTOR):
            digest = get_digest(i.to_bytes(1, byteorder='big') + NetWorkSettings.ALIAS_SEED)
            digest_int = int.from_bytes(digest, byteorder='big')
            self.__logger.debug("Alias digest %s -> %s" % (i, digest_int))
            self.__alias_digests.append(digest_int)

    def __recalculate_ownership_of_all_chunks(self):
        for chunkid in self.__chunk_table:
            self.__update_chunk_ownership(chunkid)

    def __generate_aliases(self, chunkid):
        for alias_digest in self.__alias_digests:
            yield alias_digest ^ chunkid

    def __update_chunk_ownership(self, chunkid):
        actual_chunk_is_ours = False

        # maintain the alias table
        alias_updates = []
        for alt_key in self.__generate_aliases(chunkid):
            alias_owned = self.__we_own_this_alt_key(alt_key)
            alias_updates.append((alt_key, alias_owned))

            if alias_owned:
                # if we own the alias we own the chunk
                actual_chunk_is_ours = True

        # maintain alias db
        for alt_key, alt_key_owned in alias_updates:
            if alt_key_owned:
                # this alias points to us
                # self.__logger.debug("Alt key %s is now OWNED (chunkid: %s)" % (alt_key, chunkid))
                self.__alias_db[alt_key] = chunkid
            else:
                # this alias not longer points to us
                # self.__logger.debug("Alt key %s is now DISOWNED (chunkid: %s)" % (alt_key, chunkid))
                if self.__alias_db.get(alt_key) is not None:
                    del self.__alias_db[alt_key]

        # if even a single alias says we own this chunk, we do
        if actual_chunk_is_ours:
            # maintain file db
            chunk = self.__get_or_create_chunk(chunkid)
            if not chunk.is_ours:
                # self.__logger.debug("Chunk %s is now OWNED" % chunkid)
                chunk.is_ours = True

            # if we don't have it or it's not verified for some reason, fetch it
            if not chunk.exists or not chunk.verified:
                # do we have it locally? - this can happen if we just booted up
                verified = self.__storage.verify(chunkid)

                if verified:
                    self.__logger.debug("Found chunk %s locally" % chunkid)
                    data = self.__storage.get(chunkid)
                    self.store_chunk(chunkid, data)
                else:
                    # we need to fetch the chunk
                    self.__logger.info("Chunk %s missing, added to todolist" % chunkid)
                    self.__todolist.put_nowait(("MISSING_CHUNK", chunkid))

        else:
            # maintain file db
            chunk = self.__get_or_create_chunk(chunkid, create=False)
            if chunk is not None:
                if chunk.is_ours:
                    # self.__logger.debug("Chunk %s is now DISOWNED" % chunkid)
                    chunk.is_ours = False

        return actual_chunk_is_ours

    def select_random_chunks_we_have(self, n):
        chunks_we_have = []
        for chunk_id, chunk in self.__file_db.items():
            if chunk.exists and chunk.verified and chunk.is_ours:
                chunks_we_have.append(chunk_id)

        if len(chunks_we_have) == 0:
            # we have no chunks yet
            return []

        return random.sample(chunks_we_have, n)

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

    def __we_own_this_alt_key(self, alt_key):
        my_distance = alt_key ^ self.__nodeid

        # check if we are the closest to this chunk
        store = True
        for othernodeid in self.__mn_manager.get_other_nodes(self.__nodeid):
            if alt_key ^ othernodeid < my_distance:
                store = False
                break

        return store

    def __purge_orphaned_storage_entries(self):
        self.__logger.info("Purging orphaned files")
        for chunkid, chunk in self.__file_db.items():
            if chunk.exists:
                if not chunk.is_ours or not chunk.verified:
                    self.__storage.delete(chunkid)

    def __purge_orphaned_db_entries(self):
        self.__logger.info("Purging orphaned DB entries")
        to_delete = []
        for chunkid, chunk in self.__file_db.items():
            if not chunk.exists and not chunk.is_ours:
                to_delete.append(chunkid)

        for chunkid in to_delete:
            del self.__file_db[chunkid]

    def __purge_orphaned_files(self):
        self.__logger.debug("Purging local files in %s" % self.__storagedir)

        # reads the filesystem and fills our DB of chunks we have
        for chunkid in self.__storage.index():
            chunk = self.__file_db.get(chunkid)

            if chunk is None:
                # we don't know what this file is (perhaps it used to belong to us but not anymore)
                self.__storage.delete(chunkid)

        self.__logger.debug("Discovered %s files in local storage" % len(self.__file_db))

    def __get_or_create_chunk(self, chunkid, create=True):
        if self.__file_db.get(chunkid) is None:
            if not create:
                return None
            else:
                self.__file_db[chunkid] = Chunk(chunkid=chunkid)

        chunk = self.__file_db[chunkid]
        return chunk

    def update_mn_list(self, masternode_list):
        added, removed = self.__mn_manager.update_maternode_list(masternode_list)
        if len(added) + len(removed) > 0:
            if self.__nodeid in removed:
                self.__logger.warning("I am removed from the MN list, aborting %s" % self.__nodeid)
                # return

            self.__logger.info("MN list has changed -> added: %s, removed: %s" % (added, removed))
            self.dump_internal_stats("DB STAT Before")
            self.__recalculate_ownership_of_all_chunks()
            self.__purge_orphaned_storage_entries()
            self.__purge_orphaned_db_entries()
            self.dump_internal_stats("DB STAT After")

    def store_chunk(self, chunkid, data):
        if chunkid != get_intdigest(data):
            raise ValueError("data does not match chunkid!")

        if chunkid not in self.__chunk_table:
            raise KeyError("chunkid is not in chunk_table!")

        if self.__nodeid not in self.find_owners_for_chunk(chunkid):
            raise ValueError("chunkid does not belong to us!")

        # store chunk
        self.__storage.put(chunkid, data)

        chunk = self.__get_or_create_chunk(chunkid)
        chunk.exists = True
        chunk.verified = True
        chunk.is_ours = True

        self.__update_chunk_ownership(chunkid)
        self.__logger.debug("Chunk %s is loaded" % chunkid)

    def load_full_chunks(self, chunks):
        # helper function to load chunks with data
        # this is for testing, since we have to bootstrap the system somehow
        self.dump_internal_stats("DB STAT Before")
        for chunk_str, data in chunks:

            chunkid = int(chunk_str, 16)
            self.store_chunk(chunkid, data)
            self.__logger.debug("Chunk %s is loaded" % chunkid)
        self.dump_internal_stats("DB STAT After")

    def new_chunks_added_to_blockchain(self, chunks):
        self.dump_internal_stats("DB STAT Before")
        for chunk_str in chunks:
            chunkid = int(chunk_str, 16)
            self.__chunk_table.add(chunkid)
            self.__update_chunk_ownership(chunkid)
        self.dump_internal_stats("DB STAT After")

    def get_chunk_ownership(self, chunk_str):
        chunkid = int(chunk_str, 16)
        if self.__file_db.get(chunkid) is not None:
            return self.__file_db[chunkid].is_ours
        else:
            return False

    def return_chunk_data_if_valid_and_owned_and_we_have_it(self, chunkid):
        # TODO: do error handling better here

        # check if this is an actual chunk
        if chunkid not in self.__chunk_table:
            raise ValueError("This chunk is not in the chunk table: %s" % chunkid)

        # check if we should have this chunk
        if self.__nodeid not in self.find_owners_for_chunk(chunkid):
            raise ValueError("chunk %s does not belong ot us!" % chunkid)

        # check if we have this chunk
        chunk = self.__file_db.get(chunkid)
        if chunk is None or not chunk.exists or not chunk.verified:
            # TODO: we should store this, refetch chunk?
            raise ValueError("We don't have this chunk: %s" % int_to_hex(chunkid))

        # get chunk from disk
        data = self.__storage.get(chunk.chunkid)

        # verify the chunk
        digest = get_intdigest(data)
        if digest != chunkid:
            # TODO: verify failed, refetch chunk?
            raise ValueError("Chunk's content does not match it's hash (%s != %s)" % (digest, chunkid))

        return data

    def get_chunk(self, chunkid, verify=True):
        # pick a file we have for sure
        chunk = self.__file_db[chunkid]

        if verify:
            if not self.__storage.verify(chunkid):
                # TODO: We should resync the chunk and increment some counter
                raise ValueError("Self-initiated spotcheck faield on us for chunk: %s" % chunkid)

        return self.__storage.get(chunk.chunkid)

    # DEBUG FUNCTIONS
    def dump_internal_stats(self, msg=""):
        self.__logger.debug("%s -> Aliases: %s, file_db: %s, chunk_table: %s" % (msg, len(self.__alias_db),
                                                                                 len(self.__file_db),
                                                                                 len(self.__chunk_table)))

    def dump_alias_db(self):
        for k, v in self.__alias_db.items():
            self.__logger.debug("ALIAS %s: %s" % (k, v))

    def dump_file_db(self):
        for k, v in self.__file_db.items():
            self.__logger.debug("FILE %s: %s" % (int_to_hex(k), v))
            self.__storage.get(k)
    # END