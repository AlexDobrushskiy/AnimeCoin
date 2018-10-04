import os
import asyncio
import random

from core_modules.chunk_manager import ChunkManager
from core_modules.zmq_rpc import RPCException, RPCServer
from core_modules.masternode_communication import NodeManager
from core_modules.masternode_ticketing import ArtRegistrationServer
from core_modules.helpers import get_hexdigest, get_intdigest, hex_to_int, int_to_hex, require_true


class MasterNodeLogic:
    def __init__(self, name, logger, chainwrapper, basedir, privkey, pubkey, ip, port, chunks):
        self.__name = name
        self.__nodeid = get_intdigest(pubkey)
        self.__basedir = basedir
        self.__privkey = privkey
        self.__pubkey = pubkey
        self.__ip = ip
        self.__port = port

        self.__logger = logger
        self._chainwrapper = chainwrapper

        self.__todolist = asyncio.Queue()

        # masternode manager
        # TODO: remove this hack
        nodes_basedir = os.path.dirname(os.path.dirname(self.__basedir))
        self.__mn_manager = NodeManager(self.__logger, self.__privkey, self.__pubkey, nodes_basedir)

        # chunk manager
        self.__chunkmanager = ChunkManager(self.__logger, self.__nodeid,
                                           basedir,
                                           chunks,
                                           self.__mn_manager, self.__todolist)

        # art registration server
        self.__artregistrationserver = ArtRegistrationServer(self.__privkey, self.__pubkey,
                                                             self._chainwrapper, self.__chunkmanager)

        # functions exposed from chunkmanager
        self.load_full_chunks = self.__chunkmanager.load_full_chunks

        # start rpc server
        self.__rpcserver = RPCServer(self.__logger, self.__nodeid, self.__ip, self.__port,
                                     self.__privkey, self.__pubkey)

        # TODO: the are blocking calls. We should turn them into coroutines if possible!
        # TODO: we should ACL who can access these RPCs, chunk related RPC is only for MNs!
        self.__rpcserver.add_callback("SPOTCHECK_REQ", "SPOTCHECK_RESP",
                                      self.__chunkmanager.receive_rpc_spotcheck)
        self.__rpcserver.add_callback("FETCHCHUNK_REQ", "FETCHCHUNK_RESP",
                                      self.__chunkmanager.receive_rpc_fetchchunk)

        self.__artregistrationserver.register_rpcs(self.__rpcserver)


    async def issue_random_tests_forever(self, waittime, number_of_chunks=1):
        while True:
            await asyncio.sleep(waittime)

            chunks = self.__chunkmanager.select_random_chunks_we_have(number_of_chunks)
            for chunkid in chunks:
                self.__logger.debug("Selected chunk %s for random check" % int_to_hex(chunkid))

                # get chunk
                data = self.__chunkmanager.get_chunk(chunkid, verify=True)

                # pick a random range
                require_true(len(data) > 1024)
                start = random.randint(0, len(data)-1024)
                end = start + 1024

                # calculate digest
                digest = get_hexdigest(data[start:end])
                self.__logger.debug("Digest for range %s - %s is: %s" % (start, end, digest))

                # find owners for all the alt keys who are not us
                owners = self.__chunkmanager.find_owners_for_chunk(chunkid)
                if self.__nodeid in owners:
                    # we have already tested ourselves with verify()
                    owners.remove(self.__nodeid)

                # call RPC on all other MNs
                for owner in owners:
                    mn = self.__mn_manager.get(owner)

                    try:
                        response_digest = await mn.send_rpc_spotcheck(chunkid, start, end)
                    except RPCException as exc:
                        self.__logger.info("SPOTCHECK RPC FAILED for node %s with exception %s" % (owner, exc))
                    else:
                        if response_digest != digest:
                            self.__logger.warning("SPOTCHECK FAILED for node %s (%s != %s)" % (owner, digest,
                                                                                               response_digest))
                        else:
                            self.__logger.debug("SPOTCHECK SUCCESS for node %s for chunk: %s" % (owner, digest))

                    # TODO: track successes/errors

    async def run_heartbeat_forever(self):
        while True:
            await asyncio.sleep(1)
            self.__logger.debug("HB")

    async def run_ping_test_forever(self):
        while True:
            await asyncio.sleep(1)

            mn = self.__mn_manager.get_random()
            if mn is None:
                continue

            data = b'PING'

            try:
                response_data = await mn.send_rpc_ping(data)
            except RPCException as exc:
                self.__logger.info("PING RPC FAILED for node %s with exception %s" % (mn, exc))
            else:
                if response_data != data:
                    self.__logger.warning("PING FAILED for node %s (%s != %s)" % (mn, data, response_data))
                else:
                    self.__logger.debug("PING SUCCESS for node %s for chunk: %s" % (mn, data))

                # TODO: track successes/errors

    async def run_workers_forever(self):
        # TODO: speed this up (multiple coroutines perhaps?)
        while True:
            self.__logger.debug("TODOLIST: queue size: %s" % self.__todolist.qsize())
            todoitem = await self.__todolist.get()

            itemtype, itemdata = todoitem
            if itemtype == "MISSING_CHUNK":
                chunkid = itemdata
                self.__logger.debug("Fetching chunk %s" % chunkid)

                found = False
                for owner in self.__chunkmanager.find_owners_for_chunk(chunkid):
                    if owner == self.__nodeid:
                        continue
                    mn = self.__mn_manager.get(owner)

                    try:
                        chunk = await mn.send_rpc_fetchchunk(chunkid)
                    except RPCException as exc:
                        self.__logger.info("FETCHCHUNK RPC FAILED for node %s with exception %s" % (owner, exc))
                        continue
                    else:
                        found = True
                        self.__logger.debug("Fetched chunk %s" % len(chunk))
                        break

                # nobody has this chunk
                if not found:
                    # TODO: fall back to reconstruct it from luby blocks
                    raise RuntimeError("Unable to fetch chunk %s!" % chunkid)

                # we have the chunk, store it!
                self.__chunkmanager.store_chunk(chunkid, chunk)

                # mark entry as done
                self.__todolist.task_done()
            else:
                raise ValueError("Invalid todo type: %s" % itemtype)

    async def zmq_run_forever(self):
        await self.__rpcserver.zmq_run_forever()
