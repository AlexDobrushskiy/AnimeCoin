from .helpers import bytes_from_hex, bytes_to_hex
from .ticket_models import FinalIDTicket, FinalActivationTicket, FinalRegistrationTicket


class BlockChainTicket:
    def __init__(self, tickettype, data):
        self.tickettype = tickettype
        self.data = data


class ChainWrapper:
    def __init__(self, blockchain):
        self.__blockchain = blockchain

    def get_tickets_by_type(self, tickettype):
        if tickettype not in ["identity"]:
            raise ValueError("%s is not a valid ticket type!" % tickettype)

        for txid, ticket in self.all_ticket_iterator():
            if tickettype == "identity":
                if type(ticket) == FinalIDTicket:
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
        return bytes_from_hex(self.__blockchain.getbestblockhash())

    def store_ticket(self, ticket):
        if type(ticket) == FinalIDTicket:
            identifier = b'idticket'
        elif type(ticket) == FinalRegistrationTicket:
            identifier = b'regticket'
        elif type(ticket) == FinalActivationTicket:
            identifier = b'actticket'
        else:
            raise TypeError("Ticket type invalid: %s" % type(ticket))

        encoded_data = identifier + ticket.serialize()

        return self.__blockchain.store_data_in_utxo(encoded_data)

    def retrieve_ticket(self, txid):
        raw_ticket_data = self.__blockchain.retrieve_data_from_utxo(txid)

        ticket = None
        if raw_ticket_data.startswith(b'idticket'):
            ticket = FinalIDTicket(serialized=raw_ticket_data[len(b'idticket'):])
        elif raw_ticket_data.startswith(b'regticket'):
            ticket = FinalRegistrationTicket(serialized=raw_ticket_data[len(b'regticket'):])
        elif raw_ticket_data.startswith(b'actticket'):
            ticket = FinalActivationTicket(serialized=raw_ticket_data[len(b'actticket'):])

        if ticket is None:
            raise ValueError("TXID %s is not a valid ticket: %s" % (txid, raw_ticket_data))

        return ticket

    def all_ticket_iterator(self):
        for txid in self.__blockchain.search_chain():
            try:
                ticket = self.retrieve_ticket(txid)
                # TODO: this is very slow, cache these somehow
                ticket.validate()
            except Exception as exc:
                # print("ERROR parsing txid %s: %s" % (txid, exc))
                continue
            yield txid, ticket
