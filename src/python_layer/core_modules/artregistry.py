from core_modules.logger import initlogging
from core_modules.helpers import require_true
from core_modules.settings import NetWorkSettings


class ArtWork:
    def __init__(self, artid, txid, finalactticket, regticket):
        self.artid = artid
        self.txid = txid
        self.finalactticket = finalactticket
        self.regticket = regticket


class TicketWrapper:
    def __init__(self, blockheight, artid, txid, tickettype, ticket):
        self.created = blockheight
        self.artid = artid
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
        return "art: %s, first: %s, second: %s" % (self.artid.hex(), self.first, self.second)

    def lock(self):
        self.__logger.debug("%s Tickets locked: %s, %s" % (self.artid.hex(), self.first, self.second))
        self.first.status = "locked"
        self.second.status = "locked"

    def unlock(self, success, current_block_height):
        if success:
            self.first.status = "done"
            self.first.done = True
            self.second.status = "done"
            self.second.done = True
            self.__logger.debug("%s Successful match, tickets are done: %s, %s" % (self.artid.hex(), self.first, self.second))
        else:
            # unsuccessful match, second ticket is invalidated
            self.second.status = "invalid"
            self.second.done = True
            self.__logger.debug("%s Unsuccessful match, second ticket is invalid %s, height: %s" % (
                self.artid.hex(), self.second, current_block_height))

            # check if ticket has expired
            if self.first.expired(current_block_height):
                self.first.status = "invalid"
                self.first.done = True
                self.__logger.debug("%s Unsuccessful match, first ticket expired: %s, height: %s" % (
                    self.artid.hex(), self.first, current_block_height))
            else:
                self.first.status = "open"
                self.__logger.debug("%s Unsuccessful match, first ticket remains open: %s, height: %s" % (
                    self.artid.hex(), self.first, current_block_height))

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

        unlocked_tickets = []

        # invalidate matches that expired
        newmatches = []
        for match in self.__matches:
            if match.expired(self.__current_block_height):
                # match has expired without valid transaction
                match.unlock(success=False, current_block_height=self.__current_block_height)
                self.__logger.debug("Match has expired: %s, height: %s" % (match, self.__current_block_height))

                # if match.first has not expired add it back to the matcher engine
                if match.first.done is not True:
                    unlocked_tickets.append(match.first)
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

        # add back freshly unlocked tickets to the matcher engine
        for ticket in unlocked_tickets:
            self.__find_match(ticket)

    def update_matches(self, vout):
        self.__logger.debug("Relevant transaction received: %s" % vout)
        address = vout["scriptPubKey"]["addresses"][0]
        value = vout["value"]

        found = None
        for match in self.__matches:
            if match.first.tickettype == "ask":
                ask = match.first
                bid = match.second
            else:
                ask = match.second
                bid = match.first

            if ask.ticket.wallet_address == address and ask.ticket.price == value:
                match.unlock(success=True, current_block_height=self.__current_block_height)

                # assign artwork over to the new owner
                artdb = self.__owners[match.artid]
                new_owner = bid.ticket.public_key
                if artdb.get(new_owner) is None:
                    artdb[new_owner] = 0
                artdb[new_owner] += ask.ticket.copies

                self.__logger.debug("%s Consummation successful for txid %s, %s copies reassigned!" % (
                    match.artid, ask.txid, ask.ticket.copies))
                found = match
                break

        if found is not None:
            self.__matches.remove(found)

    def get_valid_match_addresses(self):
        addresses = set()
        for match in self.__matches:
            if match.first.tickettype == "ask":
                ask = match.first
            else:
                ask = match.second
            addresses.add(ask.ticket.wallet_address)
        return addresses

    def add_artwork(self, txid, finalactticket, regticket):
        artid = regticket.imagedata_hash
        self.__artworks[artid] = ArtWork(artid, txid, finalactticket, regticket)
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
        artdb = self.__owners[artid]
        author_copies = artdb.get(ticket.public_key)

        # validate that enough copies exist
        if author_copies > ticket.copies:
            wrappedticket = TicketWrapper(self.__current_block_height, artid, txid, "transfer", ticket)
            self.__tickets[artid].append(wrappedticket)
            self.__logger.debug("Transfer ticket added to artregistry: %s" % ticket)

            # enough copies exist, transfer them
            if artdb.get(ticket.recipient) is None:
                artdb[ticket.recipient] = 0

            # move the copies
            artdb[ticket.recipient] += ticket.copies
            artdb[ticket.public_key] -= ticket.copies
            self.__logger.debug("Copies updated: %s -> %s, %s -> %s" % (ticket.recipient, artdb[ticket.recipient],
                                                                        ticket.public_key, artdb[ticket.public_key]))
            wrappedticket.done = True
            wrappedticket.status = "done"
        else:
            self.__logger.debug("Not enough copies exist %s <= %s, skipping ticket" % (author_copies, ticket.copies))

    def add_trade_ticket(self, txid, ticket):
        artid = ticket.imagedata_hash

        # lock up artworks in the trade if ask and valid
        if ticket.type == "ask":
            artdb = self.__owners[artid]
            if artdb.get(ticket.public_key) is None or ticket.copies > artdb[ticket.public_key]:
                self.__logger.debug("Artist tried to sell more art than they have, ignoring ticket!")
                return
            artdb[ticket.public_key] -= ticket.copies

        # create a new wrapped ticket
        wrappedticket = TicketWrapper(self.__current_block_height, artid, txid, "trade", ticket)
        wrappedticket.done = False
        wrappedticket.status = "open"
        self.__tickets[artid].append(wrappedticket)
        self.__logger.debug("Open trade ticket added to artregistry: %s" % ticket)

        # try to find matches for this ticket
        self.__find_match(wrappedticket)

    def __get_open_trade_tickets_for_art(self, artid):
        ret = []
        for ticket in self.__tickets[artid]:
            if ticket.tickettype == "trade" and ticket.status == "open":
                ret.append(ticket)
        return ret

    def __find_match(self, newticket):
        tickets = self.__get_open_trade_tickets_for_art(newticket.artid)
        for matchticket in tickets:
            if matchticket.ticket.price == newticket.ticket.price\
            and matchticket.ticket.copies == newticket.ticket.copies\
            and matchticket.ticket.public_key != newticket.ticket.public_key\
            and ((matchticket.ticket.type == "ask" and newticket.ticket.type == "bid") or
                 (matchticket.ticket.type == "bid" and newticket.ticket.type == "ask")):

                # match found
                self.__logger.debug("Ticket match found at price %s, copies: %s" % (
                    newticket.ticket.price, newticket.ticket.copies))

                # tickets matched, add a match object and lock
                match = Match(self.__logger, newticket.artid, matchticket, newticket, self.__current_block_height)
                match.lock()

                self.__matches.append(match)
                self.__logger.debug("Match found between %s and %s" % (matchticket.txid, newticket.txid))

                return matchticket
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
            # find the ticket with the txid
            if match.first.txid == txid or match.second.txid == txid:
                if match.first.tickettype == "ask":
                    ask = match.first
                else:
                    ask = match.second

                return ask.ticket.wallet_address, ask.ticket.price

    def get_ticket_for_artwork(self, artid):
        return self.__artworks[artid].finalactticket

    def get_all_artworks(self):
        artworks = []
        for artid, artwork in self.__artworks.items():
            artworks.append((artid, artwork.regticket.to_dict()))
        return artworks

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
