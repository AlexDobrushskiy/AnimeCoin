import os
import asyncio

from core_modules.logger import initlogging
from core_modules.artregistry import ArtRegistry
from core_modules.djangointerface import DjangoInterface
from core_modules.blockchain import NotEnoughConfirmations
from core_modules.chunkmanager import ChunkManager
from core_modules.chunkmanager_modules.chunkmanager_rpc import ChunkManagerRPC
from core_modules.chunkmanager_modules.aliasmanager import AliasManager
from core_modules.ticket_models import FinalActivationTicket, FinalTransferTicket
from core_modules.zmq_rpc import RPCException, RPCServer
from core_modules.masternode_communication import NodeManager
from core_modules.masternode_ticketing import ArtRegistrationServer
from core_modules.settings import NetWorkSettings
from core_modules.helpers import get_pynode_digest_int, get_nodeid_from_pubkey, bytes_to_chunkid, chunkid_to_hex


class MasterNodeLogic:
    def __init__(self, nodenum, blockchain, chainwrapper, basedir, privkey, pubkey, ip, port):
        self.__name = "node%s" % nodenum
        self.__nodenum = nodenum
        self.__nodeid = get_nodeid_from_pubkey(pubkey)
        self.__basedir = basedir
        self.__privkey = privkey
        self.__pubkey = pubkey
        self.__ip = ip
        self.__port = port

        self.__logger = initlogging(self.__nodenum, __name__)
        self.__blockchain = blockchain
        self.__chainwrapper = chainwrapper

        # the art registry
        self.__artregistry = ArtRegistry(self.__nodenum)

        # masternode manager
        self.__mn_manager = NodeManager(self.__nodenum, self.__privkey, self.__pubkey)

        # alias manager
        self.__aliasmanager = AliasManager(self.__nodenum, self.__nodeid, self.__mn_manager)

        # chunk manager
        self.__chunkmanager = ChunkManager(self.__nodenum, self.__nodeid, basedir, self.__aliasmanager)

        # refresh masternode list
        self.__refresh_masternode_list()

        self.__chunkmanager_rpc = ChunkManagerRPC(self.__nodenum, self.__chunkmanager, self.__mn_manager,
                                                  self.__aliasmanager)

        # art registration server
        self.__artregistrationserver = ArtRegistrationServer(self.__privkey, self.__pubkey,
                                                             self.__chainwrapper, self.__chunkmanager)

        # django interface
        self.__djangointerface = DjangoInterface(self.__privkey, self.__pubkey, self.__nodenum,
                                                 self.__artregistry, self.__chunkmanager,
                                                 self.__blockchain, self.__chainwrapper, self.__aliasmanager,
                                                 self.__mn_manager)

        # functions exposed from chunkmanager
        # self.load_full_chunks = self.__chunkmanager.load_full_chunks

        # start rpc server
        self.__rpcserver = RPCServer(self.__nodenum, self.__ip, self.__port,
                                     self.__privkey, self.__pubkey)

        # TODO: the are blocking calls. We should turn them into coroutines if possible!
        # TODO: we should ACL who can access these RPCs, chunk related RPC is only for MNs!
        self.__rpcserver.add_callback("SPOTCHECK_REQ", "SPOTCHECK_RESP",
                                      self.__chunkmanager_rpc.receive_rpc_spotcheck)
        self.__rpcserver.add_callback("FETCHCHUNK_REQ", "FETCHCHUNK_RESP",
                                      self.__chunkmanager_rpc.receive_rpc_fetchchunk)

        self.__artregistrationserver.register_rpcs(self.__rpcserver)
        self.__djangointerface.register_rpcs(self.__rpcserver)

        self.issue_random_tests_forever = self.__chunkmanager_rpc.issue_random_tests_forever

    def __refresh_masternode_list(self):
        added, removed = self.__mn_manager.update_masternode_list()
        self.__chunkmanager.update_mn_list(added, removed)

    async def run_masternode_parser(self):
        while True:
            await asyncio.sleep(1)
            self.__refresh_masternode_list()

    async def run_ticket_parser(self):
        # sleep to start fast
        await asyncio.sleep(0)

        current_block = 0
        while True:
            try:
                for txid, ticket in self.__chainwrapper.get_tickets_for_block(current_block):
                    # give others some room to breathe
                    await asyncio.sleep(0)

                    # only parse FinalActivationTickets for now
                    if type(ticket) == FinalActivationTicket:
                        # validate ticket
                        ticket.validate(self.__chainwrapper)

                        # fetch corresponding finalregticket
                        final_regticket = self.__chainwrapper.retrieve_ticket(ticket.ticket.registration_ticket_txid)

                        # get the actual regticket
                        regticket = final_regticket.ticket

                        # get the chunkids that we need to store
                        chunks = []
                        for chunkid_bytes in [regticket.thumbnailhash] + regticket.lubyhashes:
                            chunkid = bytes_to_chunkid(chunkid_bytes)
                            chunks.append(chunkid)

                        # add this chunkid to chunkmanager
                        self.__chunkmanager.add_new_chunks(chunks)

                        # add ticket to artregistry
                        self.__artregistry.add_artwork(txid, ticket, regticket)
                    elif type(ticket) == FinalTransferTicket:
                        # validate ticket
                        ticket.validate()

                        # get the transfer ticket
                        transfer_ticket = ticket.ticket
                        transfer_ticket.validate(self.__chainwrapper, self.__artregistry)

                        # add ticket to artregistry
                        self.__artregistry.add_transfer_ticket(transfer_ticket)
            except NotEnoughConfirmations:
                # this block hasn't got enough confirmations yet
                await asyncio.sleep(1)
            else:
                # successfully parsed this block
                current_block += 1
                await asyncio.sleep(.1)

    async def run_heartbeat_forever(self):
        while True:
            await asyncio.sleep(1)
            self.__chunkmanager.dump_internal_stats("HEARTBEAT")

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

    async def run_chunk_fetcher_forever(self):
        async def fetch_single_chunk_via_rpc(chunkid):
            # we need to fetch it
            found = False
            for owner in self.__aliasmanager.find_other_owners_for_chunk(chunkid):
                mn = self.__mn_manager.get(owner)

                try:
                    data = await mn.send_rpc_fetchchunk(chunkid)
                except RPCException as exc:
                    self.__logger.info("FETCHCHUNK RPC FAILED for node %s with exception %s" % (owner, exc))
                    continue

                if data is None:
                    self.__logger.info("MN %s returned None for fetchchunk %s" % (owner, chunkid))
                    # chunk was not found
                    continue

                # verify that digest matches
                digest = get_pynode_digest_int(data)
                if chunkid != digest:
                    self.__logger.info("MN %s returned bad chunk for fetchchunk %s, mismatched digest: %s" % (
                        owner, chunkid, digest))
                    continue

                # we have the chunk, store it!
                self.__chunkmanager.store_missing_chunk(chunkid, data)
                break

            # nobody has this chunk
            if not found:
                # TODO: fall back to reconstruct it from luby blocks
                self.__logger.error("Unable to fetch chunk %s, luby reconstruction is not yet implemented!" %
                                    chunkid_to_hex(chunkid))
                self.__chunkmanager.failed_to_fetch_chunk(chunkid)

        while True:
            await asyncio.sleep(0)

            missing_chunks = self.__chunkmanager.get_random_missing_chunks(NetWorkSettings.CHUNK_FETCH_PARALLELISM)

            if len(missing_chunks) == 0:
                # nothing to do, sleep a little
                await asyncio.sleep(1)
                continue

            tasks = []
            for missing_chunk in missing_chunks:
                tasks.append(fetch_single_chunk_via_rpc(missing_chunk))

            await asyncio.gather(*tasks)
            await asyncio.sleep(1)

    async def zmq_run_forever(self):
        await self.__rpcserver.zmq_run_forever()
