from core_modules.logger import initlogging
from core_modules.helpers import require_true


class ArtRegistry:
    def __init__(self, nodenum):
        self.__logger = initlogging(nodenum, __name__)
        self.__artworks = {}
        self.__tradetickets = {}
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

    def add_trade_ticket(self, ticket):
        artid = ticket.imagedata_hash
        if self.__tradetickets.get(artid) is None:
            self.__tradetickets[artid] = []
        self.__tradetickets[artid].append(ticket)
        self.__logger.debug("TradeTicket added to artregistry: %s" % ticket)

        # update owners dict
        artdb = self.__owners[artid]

        author_copies = artdb.get(ticket.public_key)
        require_true(author_copies > ticket.copies)

        if artdb.get(ticket.recipient) is None:
            artdb[ticket.recipient] = 0

        # move the copies
        artdb[ticket.recipient] += ticket.copies
        artdb[ticket.public_key] -= ticket.copies
        self.__logger.debug("Copies updated: %s -> %s, %s -> %s" % (ticket.recipient, artdb[ticket.recipient],
                                                                    ticket.public_key, artdb[ticket.public_key]))

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
