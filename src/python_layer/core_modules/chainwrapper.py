from bitcoinrpc.authproxy import JSONRPCException

from core_modules.logger import initlogging
from core_modules.helpers import bytes_from_hex, bytes_to_hex
from core_modules.ticket_models import FinalIDTicket, FinalActivationTicket, FinalRegistrationTicket,\
    FinalTransferTicket, FinalTradeTicket
from core_modules.settings import NetWorkSettings


class BlockChainTicket:
    def __init__(self, tickettype, data):
        self.tickettype = tickettype
        self.data = data


class ChainWrapper:
    def __init__(self, nodenum, blockchain):
        self.__logger = initlogging(nodenum, __name__)
        self.__blockchain = blockchain

    def get_tickets_by_type(self, tickettype):
        if tickettype not in ["identity", "regticket", "actticket", "transticket", "tradeticket"]:
            raise ValueError("%s is not a valid ticket type!" % tickettype)

        for txid, ticket in self.all_ticket_iterator():
            if tickettype == "identity":
                if type(ticket) == FinalIDTicket:
                    yield txid, ticket
            elif tickettype == "regticket":
                if type(ticket) == FinalRegistrationTicket:
                    yield txid, ticket
            elif tickettype == "actticket":
                if type(ticket) == FinalActivationTicket:
                    yield txid, ticket
            elif tickettype == "transticket":
                if type(ticket) == FinalTransferTicket:
                    yield txid, ticket
            elif tickettype == "tradeticket":
                if type(ticket) == FinalTradeTicket:
                    yield txid, ticket

    def get_identity_ticket(self, pubkey):
        for txid, ticket in self.get_tickets_by_type("identity"):
            if ticket.ticket.public_key == pubkey:
                return txid, ticket
        return None, None

    def get_block_distance(self, atxid, btxid):
        # TODO: clean up this interface
        if type(atxid) == bytes:
            atxid = bytes_to_hex(atxid)
        if type(btxid) == bytes:
            btxid = bytes_to_hex(btxid)

        block_a = self.__blockchain.getblock(atxid)
        block_b = self.__blockchain.getblock(btxid)
        height_a = int(block_a["height"])
        height_b = int(block_b["height"])
        return abs(height_a-height_b)

    def get_last_block_hash(self):
        return self.__blockchain.getbestblockhash()

    def store_ticket(self, ticket):
        if type(ticket) == FinalIDTicket:
            identifier = b'idticket'
        elif type(ticket) == FinalRegistrationTicket:
            identifier = b'regticket'
        elif type(ticket) == FinalActivationTicket:
            identifier = b'actticket'
        elif type(ticket) == FinalTransferTicket:
            identifier = b'transticket'
        elif type(ticket) == FinalTradeTicket:
            identifier = b'tradeticket'
        else:
            raise TypeError("Ticket type invalid: %s" % type(ticket))

        encoded_data = identifier + ticket.serialize()

        return self.__blockchain.store_data_in_utxo(encoded_data)

    def retrieve_ticket(self, txid, validate=False):
        try:
            raw_ticket_data = self.__blockchain.retrieve_data_from_utxo(txid)
        except JSONRPCException as exc:
            if exc.code == -8:
                # parameter 1 must be hexadecimal string
                return None
            else:
                raise

        if raw_ticket_data.startswith(b'idticket'):
            ticket = FinalIDTicket(serialized=raw_ticket_data[len(b'idticket'):])
            if validate:
                ticket.validate()
        elif raw_ticket_data.startswith(b'regticket'):
            ticket = FinalRegistrationTicket(serialized=raw_ticket_data[len(b'regticket'):])
            if validate:
                ticket.validate(self)
        elif raw_ticket_data.startswith(b'actticket'):
            ticket = FinalActivationTicket(serialized=raw_ticket_data[len(b'actticket'):])
            if validate:
                ticket.validate(self)
        elif raw_ticket_data.startswith(b'transticket'):
            ticket = FinalTransferTicket(serialized=raw_ticket_data[len(b'transticket'):])
            if validate:
                ticket.validate()
        elif raw_ticket_data.startswith(b'tradeticket'):
            ticket = FinalTradeTicket(serialized=raw_ticket_data[len(b'tradeticket'):])
            if validate:
                ticket.validate()
        else:
            raise ValueError("TXID %s is not a valid ticket: %s" % (txid, raw_ticket_data))

        return ticket

    def all_ticket_iterator(self):
        for txid in self.__blockchain.search_chain():
            try:
                ticket = self.retrieve_ticket(txid)
            except Exception as exc:
                # self.__logger.debug("ERROR parsing txid %s: %s" % (txid, exc))
                continue
            else:
                # if we didn't manage to get a good ticket back (bad txid)
                if ticket is None:
                    continue
            yield txid, ticket

    def get_tickets_for_block(self, blocknum, confirmations=NetWorkSettings.REQUIRED_CONFIRMATIONS):
        for txid in self.__blockchain.get_txids_for_block(blocknum, confirmations):
            try:
                ticket = self.retrieve_ticket(txid, validate=False)
            except Exception as exc:
                # self.__logger.debug("ERROR parsing txid %s: %s" % (txid, exc))
                continue

            yield txid, ticket
