import asyncio

import zmq
import zmq.asyncio
import uuid

from core_modules.blackbox_modules.helpers import get_sha3_512_func_hex
from .settings import NetWorkSettings
from core_modules.rpc_serialization import pack_and_sign, verify_and_unpack
from .helpers import get_hexdigest, hex_to_int, int_to_hex


class RPCException(Exception):
    pass


class RPCClient:
    def __init__(self, logger, privkey, pubkey, nodeid, server_ip, server_port, mnpubkey):
        if type(nodeid) is not int:
            raise TypeError("nodeid must be int!")

        # variables of the client
        self.__privkey = privkey
        self.__pubkey = pubkey

        # pubkey should be public
        self.pubkey = self.__pubkey

        # variables of the server (the MN)
        self.__server_nodeid = nodeid
        self.__server_ip = server_ip
        self.__server_port = server_port
        self.__server_pubkey = mnpubkey

        self.__logger = logger
        self.__zmq = None

        # TODO
        self.__reputation = None

    def __str__(self):
        return str(self.__server_nodeid)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    # TODO: unify this with the other one in MasterNodeLogic
    def __return_rpc_packet(self, sender_id, msg):
        response_packet = pack_and_sign(self.__privkey,
                                        self.__pubkey,
                                        sender_id, msg)
        return response_packet

    async def __send_rpc_and_wait_for_response(self, msg):
        ctx = zmq.asyncio.Context()
        if self.__zmq is None:
            self.__zmq = ctx.socket(zmq.DEALER)
            # TODO: make sure identity handling is correct and secure
            self.__zmq.setsockopt(zmq.IDENTITY, bytes(str(uuid.uuid4()), "utf-8"))
            self.__zmq.connect("tcp://%s:%s" % (self.__server_ip, self.__server_port))

        while True:
            try:
                await self.__zmq.send_multipart([msg], flags=zmq.NOBLOCK)
            except zmq.error.Again:
                await asyncio.sleep(0.01)
            else:
                break

        while True:
            try:
                msgs = await self.__zmq.recv_multipart(flags=zmq.NOBLOCK)  # waits for msg to be ready
            except zmq.error.Again:
                await asyncio.sleep(0.01)
            else:
                break

        if len(msgs) != 1:
            raise ValueError("msgs must be 1, we don't use multipart messages: %s" % len(msgs))

        msg = msgs[0]

        return msg

    async def __send_rpc_to_mn(self, response_name, request_packet):
        await asyncio.sleep(0)

        response_packet = await self.__send_rpc_and_wait_for_response(request_packet)

        sender_id, response_msg = verify_and_unpack(response_packet, self.__pubkey)

        rpcname, success, response_data = response_msg

        if rpcname != response_name:
            raise ValueError("Spotcheck response has rpc name: %s" % rpcname)

        if success != "SUCCESS":
            raise RPCException(response_msg)

        return response_data

    async def send_rpc_ping(self, data):
        await asyncio.sleep(0)

        request_packet = self.__return_rpc_packet(self.__server_pubkey, ["PING_REQ", data])

        returned_data = await self.__send_rpc_to_mn("PING_RESP", request_packet)

        if set(returned_data.keys()) != {"data"}:
            raise ValueError("RPC parameters are wrong for PING RESP: %s" % returned_data.keys())

        if type(returned_data["data"]) != bytes:
            raise TypeError("data is not bytes: %s" % type(returned_data["data"]))

        response_data = returned_data["data"]

        return response_data

    async def send_rpc_spotcheck(self, chunkid, start, end):
        await asyncio.sleep(0)

        self.__logger.debug("SPOTCHECK REQUEST to %s, chunkid: %s" % (self, int_to_hex(chunkid)))

        # chunkid is bignum so we need to serialize it
        chunkid_str = int_to_hex(chunkid)
        request_packet = self.__return_rpc_packet(self.__server_pubkey, ["SPOTCHECK_REQ", {"chunkid": chunkid_str,
                                                                                           "start": start,
                                                                                           "end": end}])

        response_data = await self.__send_rpc_to_mn("SPOTCHECK_RESP", request_packet)

        if set(response_data.keys()) != {"digest"}:
            raise ValueError("RPC parameters are wrong for SPOTCHECK_RESP: %s" % response_data.keys())

        if type(response_data["digest"]) != str:
            raise TypeError("digest is not str: %s" % type(response_data["digest"]))

        response_digest = response_data["digest"]

        self.__logger.debug("SPOTCHECK RESPONSE from %s, msg: %s" % (self, response_digest))

        return response_digest

    async def send_rpc_fetchchunk(self, chunkid):
        await asyncio.sleep(0)

        self.__logger.debug("FETCHCHUNK REQUEST to %s, chunkid: %s" % (self, int_to_hex(chunkid)))

        # chunkid is bignum so we need to serialize it
        chunkid_str = int_to_hex(chunkid)
        request_packet = self.__return_rpc_packet(self.__server_pubkey, ["FETCHCHUNK_REQ", {"chunkid": chunkid_str}])

        response_data = await self.__send_rpc_to_mn("FETCHCHUNK_RESP", request_packet)

        if set(response_data.keys()) != {"chunk"}:
            raise ValueError("RPC parameters are wrong for FETCHCHUNK_RESP: %s" % response_data.keys())

        if type(response_data["chunk"]) not in [bytes, type(None)]:
            raise TypeError("chunk is not bytes or None: %s" % type(response_data["chunk"]))

        chunk = response_data["chunk"]

        # validate chunk
        if chunk is not None:
            digest = get_sha3_512_func_hex(chunk)
            if digest != chunkid_str:
                raise ValueError("Got chunk data that does not match the digest!")

        return chunk

    async def __send_mn_ticket_rpc(self, rpcreq, rpcresp, data):
        await asyncio.sleep(0)
        request_packet = self.__return_rpc_packet(self.__server_pubkey, [rpcreq, data])
        returned_data = await self.__send_rpc_to_mn(rpcresp, request_packet)
        return returned_data

    async def call_masternode(self, req, resp, data):
        return await self.__send_mn_ticket_rpc(req, resp, data)


class RPCServer:
    def __init__(self, logger, nodeid, ip, port, privkey, pubkey):
        self.__logger = logger
        self.__nodeid = nodeid
        self.__ip = ip
        self.__port = port
        self.__privkey = privkey
        self.__pubkey = pubkey

        # our RPC socket
        self.__zmq = zmq.asyncio.Context().socket(zmq.ROUTER)
        self.__zmq.setsockopt(zmq.IDENTITY, bytes(str(self.__nodeid), "utf-8"))
        self.__zmq.bind("tcp://%s:%s" % (self.__ip, self.__port))

        # define our RPCs
        self.__RPCs = {}

        # add our only call
        self.add_callback("PING_REQ", "PING_RESP", self.__receive_rpc_ping)

    def add_callback(self, callback_req, callback_resp, callback_function):
        self.__RPCs[callback_req] = [callback_resp, callback_function]

    def __receive_rpc_ping(self, data):
        if not isinstance(data, bytes):
            raise TypeError("Data must be a bytes!")

        return {"data": data}

    def __return_rpc_packet(self, sender_id, msg):
        response_packet = pack_and_sign(self.__privkey,
                                        self.__pubkey,
                                        sender_id, msg)
        return response_packet

    def __process_local_rpc(self, sender_id, rpcname, data):
        self.__logger.debug("Received RPC %s" % (rpcname))
        # get the appropriate rpc function or send back an error
        rpc = self.__RPCs.get(rpcname)
        if rpc is None:
            self.__logger.info("RPC %s is not implemented, ignoring packet!" % rpcname)

        # call the RPC function, catch all exceptions
        response_name, fn = self.__RPCs.get(rpcname)
        try:
            ret = fn(data)
        except Exception as exc:
            self.__logger.exception("Exception received while doing RPC: %s" % exc)
            msg = [response_name, "ERROR", "RPC ERRROR happened: %s" % exc]
        else:
            # generate response if everything went well
            msg = [response_name, "SUCCESS", ret]

        ret = self.__return_rpc_packet(sender_id, msg)
        self.__logger.debug("Done with RPC RPC %s" % (rpcname))
        return ret

    async def __zmq_process(self, ident, msg):
        # TODO: authenticate RPC, only allow from other MNs
        sender_id, received_msg = verify_and_unpack(msg, self.__pubkey)
        rpcname, data = received_msg

        reply_packet = self.__process_local_rpc(sender_id, rpcname, data)

        while True:
            try:
                await self.__zmq.send_multipart([ident, reply_packet], flags=zmq.NOBLOCK)
            except zmq.error.Again:
                await asyncio.sleep(0.01)
            else:
                break

    async def zmq_run_once(self):
        while True:
            try:
                ident, msg = await self.__zmq.recv_multipart(flags=zmq.NOBLOCK)  # waits for msg to be ready
            except zmq.error.Again:
                await asyncio.sleep(0.01)
            else:
                break

        asyncio.ensure_future(self.__zmq_process(ident, msg))

    async def zmq_run_forever(self):
        while True:
            await self.zmq_run_once()
