import random

from .helpers import bytes_from_hex, bytes_to_hex
from .helpers_type import ensure_type
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

        block_a = self.__blockchain.jsonrpc.getblock(atxid)
        block_b = self.__blockchain.jsonrpc.getblock(btxid)
        height_a = int(block_a["height"])
        height_b = int(block_b["height"])
        return abs(height_a-height_b)

    def get_last_block_hash(self):
        return bytes_from_hex(self.__blockchain.jsonrpc.getbestblockhash())

    # BITCOIN RPCS
    def generate(self, amount):
        return self.__blockchain.jsonrpc.generate(amount)

    def listtransactions(self):
        return self.__blockchain.jsonrpc.listtransactions()
    # END

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

    def __get_masternodes_from_blockchain(self, target_txid=None):
        for txid, ticket in self.__blockchain.search_chain():
            if ticket.tickettype == "masternode":
                pubkey, mn = ticket.data[0], ticket.data[1]
                yield pubkey, mn
            if target_txid is not None and txid == target_txid:
                break

    def get_masternode_order(self, target_txid):
        # get MNs that were active at target_txid time
        masternodes = [pubkey for pubkey, mn in self.__get_masternodes_from_blockchain(target_txid)]

        # generate a reproducible sample of the MN population, then reset the random seed
        random.seed(target_txid)
        random_sample = random.sample(masternodes, 3)
        random.seed()
        # end

        random_sample.sort()
        return random_sample

    # MASTERNODE STUFF WE HAVE TO ACCESS GLOBALLY
    def register_masternode(self, pubkey, mn):
        self.__blockchain.store_data_in_utxo(tickettype="masternode", data=(pubkey, mn))

    def get_masternode(self, key):
        for pubkey, mn in self.__get_masternodes_from_blockchain():
            if pubkey == key:
                return mn
        raise KeyError("Masternode for key %s does not exist!" % key)
    # END
