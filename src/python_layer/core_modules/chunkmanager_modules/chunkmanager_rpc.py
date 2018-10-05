import random
import asyncio

from core_modules.zmq_rpc import RPCException
from core_modules.blackbox_modules.helpers import get_sha3_512_func_int, get_sha3_512_func_bytes, get_sha3_512_func_hex
from core_modules.helpers import hex_to_int, int_to_hex, require_true, get_hexdigest
from core_modules.settings import NetWorkSettings


class ChunkManagerRPC:
    def __init__(self, logger, chunkmanager, mn_manager):
        self.__logger = logger
        self.__chunkmanager = chunkmanager
        self.__mn_manager = mn_manager

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
                owners = self.__chunkmanager.find_other_owners_for_chunk(chunkid)

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

    def __return_chunk_data_if_valid_and_owned_and_we_have_it(self, chunkid):
        # TODO: do error handling better here

        # check if this is an actual chunk
        if not self.__chunkmanager.we_have_chunkid_in_chunk_table(chunkid):
            raise ValueError("This chunk is not in the chunk table: %s" % chunkid)

        # check if we should have this chunk
        if not self.__chunkmanager.we_own_chunk(chunkid):
            raise ValueError("chunk %s does not belong ot us!" % chunkid)

        # check if we have this chunk
        if not self.__chunkmanager.we_have_chunk_on_disk(chunkid):
            # TODO: we should store this, refetch chunk?
            raise ValueError("We don't have this chunk: %s" % int_to_hex(chunkid))

        # get chunk from disk
        data = self.__chunkmanager.get_chunk(chunkid)

        # verify the chunk
        digest = get_sha3_512_func_int(data)
        if digest != chunkid:
            # TODO: verify failed, refetch chunk?
            raise ValueError("Chunk's content does not match it's hash (%s != %s)" % (digest, chunkid))

        return data

    def receive_rpc_spotcheck(self, data):
        # NOTE: data is untrusted!
        if not isinstance(data, dict):
            raise TypeError("Data must be a dict!")

        if set(data.keys()) != {"chunkid", "start", "end"}:
            raise ValueError("Invalid arguments for spotcheck: %s" % (data.keys()))

        for k, v in data.items():
            if k in ["start", "end"]:
                if not isinstance(v, int):
                    raise TypeError("Invalid type for key %s in spotcheck" % k)
            else:
                if not isinstance(v, str):
                    raise TypeError("Invalid type for key %s in spotcheck" % k)

        chunkid = hex_to_int(data["chunkid"])
        start = data["start"]
        end = data["end"]

        # check if start and end are within parameters
        if start < 0:
            raise ValueError("start is < 0")
        if start >= end:
            raise ValueError("start >= end")
        if start > NetWorkSettings.CHUNKSIZE or end > NetWorkSettings.CHUNKSIZE:
            raise ValueError("start > CHUNKSIZE or end > CHUNKSIZE")

        # we don't actually need the full chunk here, but we get it anyway as we are running verify() on it
        chunk = self.__return_chunk_data_if_valid_and_owned_and_we_have_it(chunkid)

        # generate digest
        data = chunk[start:end]
        digest = get_sha3_512_func_hex(data)

        return {"digest": digest}

    def receive_rpc_fetchchunk(self, data):
        # NOTE: data is untrusted!
        if not isinstance(data, dict):
            raise TypeError("Data must be a dict!")

        if set(data.keys()) != {"chunkid"}:
            raise ValueError("Invalid arguments for spotcheck: %s" % (data.keys()))

        if not isinstance(data["chunkid"], str):
            raise TypeError("Invalid type for key chunkid in spotcheck")

        chunkid = hex_to_int(data["chunkid"])

        # TODO: error handling
        chunk = self.__return_chunk_data_if_valid_and_owned_and_we_have_it(chunkid)

        return {"chunk": chunk}
