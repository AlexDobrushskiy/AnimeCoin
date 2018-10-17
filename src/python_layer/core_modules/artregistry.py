from core_modules.logger import initlogging
from core_modules.helpers import require_true


class ArtRegistry:
    def __init__(self, nodenum):
        self.__logger = initlogging(nodenum, __name__)
        self.__artworks = {}
        self.__tradetickets = {}
        self.__owners = {}

    def add_artwork(self, ticket):
        artid = ticket.imagedata_hash
        self.__artworks[artid] = ticket
        self.__logger.debug("RegTicket added to artregistry: %s" % ticket)

        # update owner DB
        if self.__owners.get(artid) is None:
            self.__owners[artid] = {}
        artdb = self.__owners[artid]

        # assert that this artwork is not yet found
        require_true(artdb.get(ticket.author) is None)

        artdb[ticket.author] = ticket.total_copies
        self.__logger.debug("Author %s granted %s copies" % (ticket.author, ticket.total_copies))

    def add_trade_ticket(self, ticket):
        artid = ticket.imagedata_hash
        if self.__tradetickets.get(artid) is None:
            self.__tradetickets[artid] = []
        self.__tradetickets[artid].append(ticket)
        self.__logger.debug("TradeTicket added to artregistry: %s" % ticket)

        # update owners dict
        artdb = self.__owners[artid]

        author_copies = artdb.get(ticket.author)
        require_true(author_copies < ticket.copies)

        if artdb.get(ticket.recipient) is None:
            artdb[ticket.recipient] = 0

        # move the copies
        artdb[ticket.recipient] += ticket.copies
        artdb[ticket.author] -= ticket.copies
        self.__logger.debug("Copies updated: %s -> %s, %s -> %s" % (ticket.recipient, artdb[ticket.recipient],
                                                                    ticket.author, artdb[ticket.author]))

    def enough_copies_left(self, artid, author, copies):
        artdb = self.__owners.get(artid)
        if artdb is None:
            return False

        author_copies = artdb.get(author)
        if author_copies is None or author_copies < copies:
            return False

        return True
