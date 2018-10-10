import os
import random

from core_modules.blackbox_modules.helpers import get_sha3_512_func_bytes, get_sha3_512_func_hex, get_sha3_512_func_int
from core_modules.chunk_storage import ChunkStorage
from core_modules.helpers import hex_to_int, chunkid_to_hex
from core_modules.logger import initlogging


class Chunk:
    def __init__(self, chunkid, exists=False, verified=False, is_ours=False):
        if type(chunkid) != int:
            raise ValueError("chunkid is not int!")

        self.chunkid = chunkid
        self.exists = exists
        self.verified = verified
        self.is_ours = is_ours

    def __str__(self):
        return "chunkid: %s, exists: %s, verified: %s, is_ours: %s" % (chunkid_to_hex(self.chunkid), self.exists,
                                                                       self.verified, self.is_ours)


class ChunkManager:
    def __init__(self, nodenum, nodeid, basedir, chunks, aliasmanager, todolist):
        # initialize logger
        # IMPORTANT: we must ALWAYS use self.__logger.* for logging and not logging.*,
        # since we need instance-level logging
        self.__logger = initlogging(nodenum, __name__)

        # our node id
        self.__nodeid = nodeid

        # the actual storage layer
        self.__storagedir = os.path.join(basedir, "chunkdata")
        self.__storage = ChunkStorage(self.__storagedir, mode=0o0700)

        # alias manager
        self.__alias_manager = aliasmanager

        # databases we keep
        self.__alias_db = {}
        self.__file_db = {}

        # table of every chunk we know of
        self.__chunk_table = set((hex_to_int(x) for x in chunks))

        # tmp storage
        self.__tmpstoragedir = os.path.join(basedir, "tmpstorage")
        self.__tmpstorage = ChunkStorage(self.__tmpstoragedir, mode=0o0700)

        # todolist
        self.__todolist = todolist

        # run other initializations
        self.__initialize()

    def __str__(self):
        return "%s" % self.__nodeid

    def __initialize(self):
        self.__logger.debug("Initializing")

        # initializations
        self.__recalculate_ownership_of_all_chunks()
        self.__purge_orphaned_storage_entries()
        self.__purge_orphaned_db_entries()
        self.__purge_orphaned_files()
        self.dump_internal_stats()

    def __recalculate_ownership_of_all_chunks(self):
        for chunkid in self.__chunk_table:
            self.__update_chunk_ownership(chunkid)

    def __update_chunk_ownership(self, chunkid):
        alias_updates = self.__alias_manager.calculate_alias_updates(chunkid)

        # maintain alias db
        # TODO: are we sure old entries will not accumulate here?

        actual_chunk_is_ours = False
        for alt_key, alt_key_owned in alias_updates:
            if alt_key_owned:
                # this alias points to us
                # self.__logger.debug("Alt key %s is now OWNED (chunkid: %s)" % (alt_key, chunkid))
                self.__alias_db[alt_key] = chunkid

                # if we own the alias we own the chunk
                actual_chunk_is_ours = True
            else:
                # this alias no longer points to us
                # self.__logger.debug("Alt key %s is now DISOWNED (chunkid: %s)" % (alt_key, chunkid))
                if self.__alias_db.get(alt_key) is not None:
                    del self.__alias_db[alt_key]

        # if even a single alias says we own this chunk, we do
        if actual_chunk_is_ours:
            # maintain file db
            chunk = self.__get_or_create_chunk(chunkid)
            if not chunk.is_ours:
                # self.__logger.debug("Chunk %s is now OWNED" % chunkid_to_hex(chunkid))
                chunk.is_ours = True

            # if we don't have it or it's not verified for some reason, fetch it
            if not chunk.exists or not chunk.verified:
                data = None

                # do we have it locally? - this can happen if we just booted up
                if self.__storage.verify(chunkid):
                    self.__logger.debug("Found chunk %s locally" % chunkid_to_hex(chunkid))
                    data = self.__storage.get(chunkid)

                # do we have it in tmp storage?
                if data is None:
                    if self.__tmpstorage.verify(chunkid):
                        data = self.__tmpstorage.get(chunkid)
                        self.__logger.debug("Found chunk %s in temporary storage" % chunkid_to_hex(chunkid))

                # did we find the data?
                if data is not None:
                    self.store_missing_chunk(chunkid, data)
                else:
                    # we need to fetch the chunk using RPC
                    self.__logger.info("Chunk %s missing, added to todolist" % chunkid_to_hex((chunkid)))
                    self.__add_missing_chunk_to_todolist(chunkid)
        else:
            # maintain file db
            chunk = self.__get_or_create_chunk(chunkid, create=False)
            if chunk is not None:
                if chunk.is_ours:
                    self.__logger.debug("Chunk %s is now DISOWNED" % chunkid)
                    chunk.is_ours = False

        return actual_chunk_is_ours

    def __add_missing_chunk_to_todolist(self, chunkid):
        self.__todolist.put_nowait(("MISSING_CHUNK", chunkid_to_hex(chunkid)))

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

    def select_random_chunks_we_have(self, n):
        chunks_we_have = []
        for chunk_id, chunk in self.__file_db.items():
            if chunk.exists and chunk.verified and chunk.is_ours:
                chunks_we_have.append(chunk_id)

        if len(chunks_we_have) == 0:
            # we have no chunks yet
            return []

        return random.sample(chunks_we_have, n)

    def update_mn_list(self, added, removed):
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

    def add_chunks(self, chunks):
        self.dump_internal_stats("DB STAT Before")
        for chunkid in chunks:
            self.__chunk_table.add(chunkid)
            self.__update_chunk_ownership(chunkid)
        self.dump_internal_stats("DB STAT After")

    def store_chunk_provisionally(self, chunkid, data):
        if chunkid != get_sha3_512_func_int(data):
            raise ValueError("data does not match chunkid!")

        self.__tmpstorage.put(chunkid, data)

    def store_missing_chunk(self, chunkid, data):
        if chunkid != get_sha3_512_func_int(data):
            raise ValueError("data does not match chunkid!")

        if chunkid not in self.__chunk_table:
            raise KeyError("chunkid is not in chunk_table!")

        if not self.__alias_manager.we_own_chunk(chunkid):
            raise ValueError("chunkid does not belong to us!")

        # store chunk
        self.__storage.put(chunkid, data)

        chunk = self.__get_or_create_chunk(chunkid)
        chunk.exists = True
        chunk.verified = True
        chunk.is_ours = True

        self.__logger.debug("Chunk %s is loaded" % chunkid)

    # def load_full_chunks(self, chunks):
    #     # helper function to load chunks with data
    #     # this is for testing, since we have to bootstrap the system somehow
    #     self.dump_internal_stats("DB STAT Before")
    #     for chunk_str, data in chunks:
    #
    #         chunkid = int(chunk_str, 16)
    #         self.store_missing_chunk(chunkid, data)
    #         self.__logger.debug("Chunk %s is loaded" % chunkid)
    #     self.dump_internal_stats("DB STAT After")

    # def get_chunk_ownership(self, chunk_str):
    #     chunkid = int(chunk_str, 16)
    #     if self.__file_db.get(chunkid) is not None:
    #         return self.__file_db[chunkid].is_ours
    #     else:
    #         return False

    def get_chunk(self, chunkid):
        if not self.__alias_manager.we_own_chunk(chunkid):
            raise ValueError("We don't own this chunk!")

        chunk = self.__file_db.get(chunkid)

        # try to find chunk in chunkstorage
        if chunk is not None and chunk.exists and chunk.verified:
            return self.__storage.get(chunkid)

        # fall back to try and find chunk in tmpstorage
        #  - for tickets that are registered through us, but not final on the blockchain yet, this is how we bootstrap
        #  - we are also graceful and can return chunks that are not ours...
        if self.__tmpstorage.verify(chunkid):
            return self.__tmpstorage.get(chunkid)

        # we have failed to find the chunk, add an item for our todolist
        self.__logger.warning("We don't have a chunk available that we should have: %s" % chunkid_to_hex(chunkid))
        self.__add_missing_chunk_to_todolist(chunkid)

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
            self.__logger.debug("FILE %s: %s" % (chunkid_to_hex(k), v))
            self.__storage.get(k)
    # END
