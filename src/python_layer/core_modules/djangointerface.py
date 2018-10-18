import asyncio

from bitcoinrpc.authproxy import JSONRPCException

from core_modules.masternode_ticketing import ArtRegistrationClient, IDRegistrationClient
from core_modules.logger import initlogging
from core_modules.helpers import bytes_to_chunkid, hex_to_chunkid


class DjangoInterface:
    def __init__(self, privkey, pubkey, nodenum, artregistry, chunkmanager, blockchain,
                 chainwrapper, aliasmanager, nodemanager):

        self.__logger = initlogging(nodenum, __name__)

        self.__privkey = privkey
        self.__pubkey = pubkey

        self.__artregistry = artregistry
        self.__chunkmanager = chunkmanager
        self.__blockchain = blockchain
        self.__chainwrapper = chainwrapper
        self.__aliasmanager = aliasmanager
        self.__nodemanager = nodemanager

    def register_rpcs(self, rpcserver):
        # TODO: check that these RPC can only come from us, otherwise this is a massive security vulnerability
        rpcserver.add_callback("DJANGO_REQ", "DJANGO_RESP", self.process_django_request, coroutine=True)

    async def process_django_request(self, data):
        rpcname = data[0]
        args = data[1:]
        self.__logger.debug("Received Django RPC: %s, args: %s" % (rpcname, args))

        if rpcname == "get_info":
            return self.__get_infos()
        elif rpcname == "ping_masternodes":
            return await self.__ping_masternodes()
        elif rpcname == "get_chunk":
            return await self.__get_chunk_id(args[0])
        elif rpcname == "browse":
            return self.__browse(args[0])
        elif rpcname == "get_wallet_info":
            return self.__get_wallet_info()
        elif rpcname == "send_to_address":
            return self.__send_to_address(*args)
        elif rpcname == "register_image":
            return await self.__register_image(*args)
        elif rpcname == "get_identities":
            return self.__get_identities(args[0])
        elif rpcname == "register_identity":
            return self.__register_identity(args[0])
        elif rpcname == "execute_console_command":
            return self.__execute_console_command(args[0], args[1:])
        elif rpcname == "explorer_get_chaininfo":
            return self.__explorer_get_chaininfo()
        elif rpcname == "explorer_get_block":
            return self.__explorer_get_block(args[0])
        elif rpcname == "explorer_gettransaction":
            return self.__explorer_gettransaction(args[0])
        elif rpcname == "explorer_getaddresses":
            return self.__explorer_getaddresses(args[0])
        else:
            raise ValueError("Invalid RPC: %s" % rpcname)

    def __get_infos(self):
        infos = {}
        for name in ["getblockchaininfo", "getmempoolinfo", "gettxoutsetinfo", "getmininginfo",
                     "getnetworkinfo", "getpeerinfo", "getwalletinfo"]:
            infos[name] = getattr(self.__blockchain, name)()

        infos["mnsync"] = self.__blockchain.mnsync("status")
        return infos

    async def __ping_masternodes(self):
        masternodes = self.__nodemanager.get_all()

        tasks = []
        for mn in masternodes:
            tasks.append(mn.send_rpc_ping(b'PING'))

        ret = await asyncio.gather(*tasks)
        return ret

    async def __get_chunk_id(self, chunkid_hex):
        chunkid = hex_to_chunkid(chunkid_hex)

        image_data = None

        # find MNs that have this chunk
        owners = self.__aliasmanager.find_other_owners_for_chunk(chunkid)
        for owner in owners:
            mn = self.__nodemanager.get(owner)

            image_data = await mn.send_rpc_fetchchunk(chunkid)

            if image_data is not None:
                break

        return image_data

    def __browse(self, txid):
        tickets, regticket, lubyhashes = [], None, []
        if txid == "":
            for tmptxid, final_actticket in self.__chainwrapper.get_tickets_by_type("actticket"):
                final_actticket.validate(self.__chainwrapper)
                final_regticket = self.__chainwrapper.retrieve_ticket(final_actticket.ticket.registration_ticket_txid)
                final_regticket.validate(self.__chainwrapper)
                regticket = final_regticket.ticket
                tickets.append((tmptxid, regticket.to_dict()))

        else:
            # get and process ticket as new node
            final_actticket = self.__chainwrapper.retrieve_ticket(txid)
            final_actticket.validate(self.__chainwrapper)
            final_regticket = self.__chainwrapper.retrieve_ticket(final_actticket.ticket.registration_ticket_txid)
            final_regticket.validate(self.__chainwrapper)
            regticket = final_regticket.ticket
        return tickets, regticket.to_dict()

    def __get_wallet_info(self):
        listunspent = self.__blockchain.listunspent()
        receivingaddress = self.__blockchain.getaccountaddress("")
        balance = self.__blockchain.getbalance()
        return listunspent, receivingaddress, balance

    def __send_to_address(self, address, amount):
        try:
            self.__blockchain.sendtoaddress(address, amount)
        except JSONRPCException as exc:
            return str(exc)
        else:
            return None

    async def __register_image(self, image_field, image_data):
        # get the registration object
        artreg = ArtRegistrationClient(self.__privkey, self.__pubkey, self.__chainwrapper, self.__nodemanager)

        # register image
        # TODO: fill these out properly
        task = artreg.register_image(
            image_data=image_data,
            artist_name="Example Artist",
            artist_website="exampleartist.com",
            artist_written_statement="This is only a test",
            artwork_title=image_field,
            artwork_series_name="Examples and Tests collection",
            artwork_creation_video_youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            artwork_keyword_set="example, testing, sample",
            total_copies=10
        )

        result = await task
        actticket_txid = result
        final_actticket = self.__chainwrapper.retrieve_ticket(actticket_txid, validate=True)
        return actticket_txid, final_actticket.to_dict()

    def __get_identities(self, pubkey):
        addresses = []
        for unspent in self.__blockchain.listunspent():
            if unspent["address"] not in addresses:
                addresses.append(unspent["address"])

        identity_txid, identity_ticket = self.__chainwrapper.get_identity_ticket(pubkey)
        all_identities = list(
            (txid, ticket.to_dict()) for txid, ticket in self.__chainwrapper.get_tickets_by_type("identity"))
        return addresses, all_identities, identity_txid, identity_ticket.to_dict()

    def __register_identity(self, address):
        regclient = IDRegistrationClient(self.__privkey, self.__pubkey, self.__chainwrapper)
        regclient.register_id(address)

    def __execute_console_command(self, cmdname, cmdargs):
        command_rpc = getattr(self.__blockchain, cmdname)
        try:
            result = command_rpc(*cmdargs)
        except JSONRPCException as exc:
            return False, "EXCEPTION: %s" % exc
        else:
            return True, result

    def __explorer_get_chaininfo(self):
        return self.__blockchain.getblockchaininfo()

    def __explorer_get_block(self, blockid):
        blockcount, block = None, None

        blockcount = self.__blockchain.getblockcount() - 1
        if blockid != "":
            try:
                block = self.__blockchain.getblock(blockid)
            except JSONRPCException:
                block = None

        return blockcount, block

    def __explorer_gettransaction(self, transactionid):
        transaction = None
        try:
            if transactionid == "":
                transaction = self.__blockchain.listsinceblock()["transactions"][-1]
            else:
                transaction = self.__blockchain.gettransaction(transactionid)
        except JSONRPCException:
            pass
        return transaction

    def __explorer_getaddresses(self, addressid):
        transactions = None
        try:
            if addressid != "":
                transactions = self.__blockchain.listunspent(1, 999999999, [addressid])
            else:
                transactions = self.__blockchain.listunspent(1, 999999999)
        except JSONRPCException:
            pass
        return transactions
