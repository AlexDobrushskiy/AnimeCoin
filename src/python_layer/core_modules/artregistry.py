from core_modules.logger import initlogging
from core_modules.helpers import require_true


class TicketWrapper:
    def __init__(self, txid, tickettype, ticket):
        self.txid = txid
        self.ticket = ticket
        self.tickettype = tickettype
        self.valid = None


class ArtRegistry:
    def __init__(self, nodenum):
        self.__logger = initlogging(nodenum, __name__)
        self.__artworks = {}
        self.__tickets = {}
        self.__owners = {}

    def add_artwork(self, txid, finalactticket, regticket):
        artid = regticket.imagedata_hash
        self.__artworks[artid] = (txid, finalactticket)
        self.__logger.debug("FinalActivationTicket added to artregistry: %s" % finalactticket)

        # update owner DB
        if self.__owners.get(artid) is None:
            self.__owners[artid] = {}
        artdb = self.__owners[artid]

        # assert that this artwork is not yet found
        require_true(artdb.get(regticket.author) is None)

        artdb[regticket.author] = regticket.total_copies
        self.__logger.debug("Author %s granted %s copies" % (regticket.author, regticket.total_copies))

    def add_transfer_ticket(self, txid, ticket):
        artid = ticket.imagedata_hash

        # collect trade tickets for debug purposes
        if self.__tickets.get(artid) is None:
            self.__tickets[artid] = []

        wrappedticket = TicketWrapper(txid, "transfer", ticket)
        self.__tickets[artid].append(wrappedticket)
        self.__logger.debug("Transfer ticket added to artregistry: %s" % ticket)

        artdb = self.__owners[artid]
        author_copies = artdb.get(ticket.public_key)

        # validate that enough copies exist
        if author_copies > ticket.copies:
            # enough copies exist, transfer them
            if artdb.get(ticket.recipient) is None:
                artdb[ticket.recipient] = 0

            # move the copies
            artdb[ticket.recipient] += ticket.copies
            artdb[ticket.public_key] -= ticket.copies
            self.__logger.debug("Copies updated: %s -> %s, %s -> %s" % (ticket.recipient, artdb[ticket.recipient],
                                                                        ticket.public_key, artdb[ticket.public_key]))
            wrappedticket.valid = True
        else:
            self.__logger.debug("Not enough copies exist %s <= %s, skipping ticket" % (author_copies, ticket.copies))
            wrappedticket.valid = False

    def add_trade_ticket(self, txid, ticket):
        artid = ticket.imagedata_hash

        # collect trade tickets for debug purposes
        if self.__tickets.get(artid) is None:
            self.__tickets[artid] = []

        wrappedticket = TicketWrapper(txid, "trade", ticket)
        self.__tickets[artid].append(wrappedticket)
        self.__logger.debug("Trade ticket added to artregistry: %s" % ticket)

        # TODO

        # artdb = self.__owners[artid]
        # author_copies = artdb.get(ticket.public_key)
        #
        # # validate that enough copies exist
        # if author_copies > ticket.copies:
        #     # enough copies exist, transfer them
        #     if artdb.get(ticket.recipient) is None:
        #         artdb[ticket.recipient] = 0
        #
        #     # move the copies
        #     artdb[ticket.recipient] += ticket.copies
        #     artdb[ticket.public_key] -= ticket.copies
        #     self.__logger.debug("Copies updated: %s -> %s, %s -> %s" % (ticket.recipient, artdb[ticket.recipient],
        #                                                                 ticket.public_key, artdb[ticket.public_key]))
        #     wrappedticket.valid = True
        # else:
        #     self.__logger.debug("Not enough copies exist %s <= %s, skipping ticket" % (author_copies, ticket.copies))
        #     wrappedticket.valid = False

    def enough_copies_left(self, artid, author, copies):
        artdb = self.__owners.get(artid)
        if artdb is None:
            return False

        author_copies = artdb.get(author)
        if author_copies is None or author_copies < copies:
            return False

        return True

    def get_art_owned_by(self, pubkey):
        artworks = []
        for artid, owners in self.__owners.items():
            for owner, copies in owners.items():
                if owner == pubkey:
                    artworks.append((artid, copies))
        return artworks

    def get_ticket_for_artwork(self, artid):
        return self.__artworks[artid][1]

    def get_art_owners(self, artid):
        artdb = self.__owners.get(artid)
        if artdb is None:
            return None

        return artdb.copy()

    def get_art_trade_tickets(self, artid):
        tradetickets = self.__tickets.get(artid)
        if tradetickets is None:
            return None

        ret = []
        for ticketwrapper in tradetickets:
            ret.append((ticketwrapper.txid, ticketwrapper.valid, ticketwrapper.tickettype, ticketwrapper.ticket.to_dict()))
        return ret
