from core_modules.logger import initlogging
from core_modules.helpers import require_true
from core_modules.settings import NetWorkSettings


class TicketWrapper:
    def __init__(self, blockheight, txid, tickettype, ticket):
        self.created = blockheight
        self.txid = txid
        self.ticket = ticket
        self.tickettype = tickettype
        self.status = None                          # open, locked, done, invalid
        self.done = None

    def __str__(self):
        return "TXID: %s" % self.txid

    def expired(self, current_block_height):
        require_true(self.tickettype == "trade")

        if self.ticket.expiration != 0:
            blocks_elapsed = current_block_height - self.created
            if blocks_elapsed > self.ticket.expiration:
                return True
        return False


class Match:
    def __init__(self, logger, artid, first, second, lockstart):
        # order is important here: first is always the ticket that comes first!
        self.__logger = logger

        self.artid = artid
        self.first = first
        self.second = second

        # these two variables mark the block numbers in between which this match is considered valid
        self.lockstart = lockstart
        self.lockend = lockstart + NetWorkSettings.TICKET_MATCH_EXPIRY

    def __str__(self):
        return "first: %s, second: %s" % (self.first, self.second)

    def lock(self):
        self.__logger.debug("Tickets locked: %s, %s" % (self.first, self.second))
        self.first.status = "locked"
        self.second.status = "locked"

    def unlock(self, success, current_block_height):
        if success:
            self.first.status = "done"
            self.first.done = True
            self.second.status = "done"
            self.second.done = True
            self.__logger.debug("Successful match, tickets are done: %s, %s" % (self.first, self.second))
        else:
            # unsuccessful match, second ticket is invalidated
            self.second.status = "invalid"
            self.second.done = True
            self.__logger.debug("Unsuccessful match, second ticket is invalid %s" % self.second)

            # check if ticket has expired
            if self.first.expired(current_block_height):
                self.first.status = "invalid"
                self.first.done = True
                self.__logger.debug("Unsuccessful match, first ticket expired: %s" % self.first)
            else:
                self.first.status = "open"
                self.__logger.debug("Unsuccessful match, first ticket remains open: %s" % self.first)

    def expired(self, current_block_height):
        if current_block_height > self.lockend:
            return True
        return False


class ArtRegistry:
    def __init__(self, nodenum):
        self.__logger = initlogging(nodenum, __name__)
        self.__artworks = {}
        self.__tickets = {}
        self.__owners = {}
        self.__matches = []
        self.__current_block_height = None

    def update_current_block_height(self, new_height):
        self.__current_block_height = new_height

        # invalidate matches that expired
        newmatches = []
        for match in self.__matches:
            if match.expired(self.__current_block_height):
                # match has expired without valid transaction
                match.unlock(success=False, current_block_height=self.__current_block_height)
                self.__logger.debug("Match has expired: %s" % match)
            else:
                newmatches.append(match)
        self.__matches = newmatches

        # invalidate open tickets (only these can expire)
        for artid in self.__artworks.keys():
            for ticket in self.__get_open_trade_tickets_for_art(artid):
                if ticket.expired(self.__current_block_height):
                    ticket.status = "invalid"
                    ticket.done = True

                    # unlock the copies
                    artdb = self.__owners[artid]
                    artdb[ticket.ticket.public_key] += ticket.ticket.copies

                    self.__logger.debug("Ticket has expired: %s" % ticket)

    def update_matches(self, vout):
        self.__logger.debug("Relevant transaction received: %s" % vout)
        address = vout["scriptPubKey"]["addresses"][0]
        value = vout["value"]

        found = None
        for match in self.__matches:
            if match.first.ticket.wallet_address == address and match.first.ticket.price == value:
                match.unlock(success=True, current_block_height=self.__current_block_height)

                # assign artwork over to the new owner
                artdb = self.__owners[match.artid]
                new_owner = match.second.ticket.public_key
                if artdb.get(new_owner) is None:
                    artdb[new_owner] = 0
                artdb[new_owner] += match.first.ticket.copies

                self.__logger.debug("Consummation successful for txid %s, %s copies reassigned!" % (match.first.txid,
                                                                                                    match.first.ticket.copies))
                found = match
                break

        if found is not None:
            self.__matches.remove(found)

    def get_valid_match_addresses(self):
        addresses = set()
        for match in self.__matches:
            addresses.add(match.first.ticket.wallet_address)
        return addresses

    def add_artwork(self, txid, finalactticket, regticket):
        artid = regticket.imagedata_hash
        self.__artworks[artid] = (txid, finalactticket)
        self.__logger.debug("FinalActivationTicket added to artregistry: %s" % finalactticket)

        # update owner DB
        if self.__owners.get(artid) is None:
            self.__owners[artid] = {}
            self.__tickets[artid] = []
        artdb = self.__owners[artid]

        # assert that this artwork is not yet found
        require_true(artdb.get(regticket.author) is None)

        artdb[regticket.author] = regticket.total_copies
        self.__logger.debug("Author %s granted %s copies" % (regticket.author, regticket.total_copies))

    def add_transfer_ticket(self, txid, ticket):
        artid = ticket.imagedata_hash

        wrappedticket = TicketWrapper(self.__current_block_height, txid, "transfer", ticket)
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
            wrappedticket.done = True
        else:
            self.__logger.debug("Not enough copies exist %s <= %s, skipping ticket" % (author_copies, ticket.copies))
            wrappedticket.done = False

    def add_trade_ticket(self, txid, ticket):
        artid = ticket.imagedata_hash

        # create a new wrapped ticket
        newticket = TicketWrapper(self.__current_block_height, txid, "trade", ticket)
        newticket.done = False
        self.__tickets[artid].append(newticket)

        matchedticket = self.__find_match(artid, ticket)
        if matchedticket is None:
            # no match
            newticket.status = "open"

            # lock up artworks in the trade
            artdb = self.__owners[artid]
            if ticket.copies > artdb[ticket.public_key]:
                self.__logger.debug("Artist tried to sell more art than they have, ignoring ticket!")
                return
            artdb[ticket.public_key] -= ticket.copies

            self.__logger.debug("Open trade ticket added to artregistry: %s" % ticket)
        else:
            # tickets matched, add a match object and lock
            match = Match(self.__logger, artid, matchedticket, newticket, self.__current_block_height)
            match.lock()

            self.__matches.append(match)
            self.__logger.debug("Match found between %s and %s" % (matchedticket.ticket, newticket.ticket))

    def __get_open_trade_tickets_for_art(self, artid):
        ret = []
        for ticket in self.__tickets[artid]:
            if ticket.tickettype == "trade" and ticket.status == "open":
                ret.append(ticket)
        return ret

    def __find_match(self, artid, newticket):
        tickets = self.__get_open_trade_tickets_for_art(artid)
        for wrappedticket in tickets:
            if wrappedticket.ticket.price == newticket.price\
            and wrappedticket.ticket.copies == newticket.copies\
            and wrappedticket.ticket.public_key != newticket.public_key:
                self.__logger.debug("Ticket match found at price %s, copies: %s" % (newticket.price, newticket.copies))
                return wrappedticket
        return None

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

    def get_my_trades(self, pubkey):
        ret = []
        for artid in self.__artworks.keys():
            for ticketwrapper in self.__tickets[artid]:
                if ticketwrapper.ticket.public_key == pubkey:
                    ret.append(self.__ticket_to_django_format(ticketwrapper))
        return ret

    def get_information_for_consummation(self, txid):
        for match in self.__matches:
            price = match.first.ticket.price
            if match.first.txid == txid:
                return match.second.ticket.wallet_address, price
            elif match.second.txid == txid:
                return match.first.ticket.wallet_address, price

    def get_ticket_for_artwork(self, artid):
        return self.__artworks[artid][1]

    def get_art_owners(self, artid):
        artdb = self.__owners.get(artid)
        if artdb is None:
            return {}

        return artdb.copy()

    def get_art_trade_tickets(self, artid):
        tradetickets = self.__tickets.get(artid)
        if tradetickets is None:
            return None

        ret = []
        for ticketwrapper in tradetickets:
            ret.append(self.__ticket_to_django_format(ticketwrapper))
        return ret

    def __ticket_to_django_format(self, ticketwrapper):
        return (ticketwrapper.created, ticketwrapper.txid, ticketwrapper.done, ticketwrapper.status,
                ticketwrapper.tickettype, ticketwrapper.ticket.to_dict())
