import time

from .ticket_models import RegistrationTicket, Signature, FinalRegistrationTicket, ActivationTicket,\
    FinalActivationTicket, ImageData, IDTicket, FinalIDTicket
from core_modules.blackbox_modules.keys import id_keypair_generation_func
from core_modules.blackbox_modules.signatures import\
    pastel_id_write_signature_on_data_func
from core_modules.chainwrapper import ChainWrapper
from core_modules.helpers import require_true


class ArtRegistrationServer:
    def __init__(self, blockchain, chunkstorage):
        self.__priv, self.__pub = id_keypair_generation_func()
        self.__chainwrapper = ChainWrapper(blockchain)
        self.__chunkstorage = chunkstorage

        # register on blockchain
        # TODO: implement this
        # self.__chainwrapper.store_ticket(self.__pub)
        self.__chainwrapper.register_masternode(self.__pub, self)

    def masternode_sign_registration_ticket(self, signature_serialized, regticket_serialized):
        # parse inputs
        signed_regticket = Signature(serialized=signature_serialized)
        regticket = RegistrationTicket(serialized=regticket_serialized)

        # validate client's signature on the ticket
        require_true(signed_regticket.pubkey == regticket.author)
        signed_regticket.validate(regticket)

        # validate registration ticket
        regticket.validate(self.__chainwrapper)

        # sign regticket
        ticket_signed_by_mn = Signature(dictionary={
            "signature": pastel_id_write_signature_on_data_func(regticket_serialized, self.__priv, self.__pub),
            "pubkey": self.__pub,
        })
        return ticket_signed_by_mn.serialize()

    def masternode_sign_activation_ticket(self, signature_serialized, activationticket_serialized, image_serialized):
        # parse inputs
        signed_actticket = Signature(serialized=signature_serialized)
        image = ImageData(serialized=image_serialized)
        activation_ticket = ActivationTicket(serialized=activationticket_serialized)

        # validate client's signature on the ticket - so only original client can activate
        require_true(signed_actticket.pubkey == activation_ticket.author)
        signed_actticket.validate(activation_ticket)

        # validate activation ticket
        activation_ticket.validate(self.__chainwrapper, image)

        # sign activation ticket
        ticket_signed_by_mn = Signature(dictionary={
            "signature": pastel_id_write_signature_on_data_func(activationticket_serialized, self.__priv, self.__pub),
            "pubkey": self.__pub,
        })
        return ticket_signed_by_mn.serialize()

    def masternode_place_ticket_on_blockchain(self, ticket, tickettype):
        # validate signed ticket
        ticket.validate(self.__chainwrapper)

        # place ticket on the blockchain
        return self.__chainwrapper.store_ticket(ticket.serialize())

    def masternode_place_image_data_in_chunkstorage(self, regticket_txid, imagedata_serialized):
        imagedata = ImageData(serialized=imagedata_serialized)
        image_hash = imagedata.get_thumbnail_hash()

        # verify that this is an actual image that is being registered
        final_regticket_serialized = self.__chainwrapper.retrieve_ticket(regticket_txid)
        final_regticket = FinalRegistrationTicket(serialized=final_regticket_serialized)
        final_regticket.validate(self.__chainwrapper)

        # store thumbnail
        self.__chunkstorage.set(image_hash, imagedata.thumbnail)

        # store chunks
        for chunkhash, chunkdata in zip(imagedata.get_luby_hashes(), imagedata.lubychunks):
            self.__chunkstorage.set(chunkhash, chunkdata)


class ArtRegistrationClient:
    def __init__(self, privkey, pubkey, blockchain):
        self.__blockchain = blockchain
        self.__chainwrapper = ChainWrapper(blockchain)

        # get MN ordering
        self.__privkey = privkey
        self.__pubkey = pubkey

    def __generate_signed_ticket(self, ticket):
        signed_ticket = Signature(dictionary={
            "signature": pastel_id_write_signature_on_data_func(ticket.serialize(), self.__privkey, self.__pubkey),
            "pubkey": self.__pubkey,
        })

        # make sure we validate correctly
        signed_ticket.validate(ticket)
        return signed_ticket

    def __generate_final_ticket(self, cls, ticket, signature, mn_signatures):
        # create combined registration ticket
        final_ticket = cls(dictionary={
            "ticket": ticket.to_dict(),
            "signature_author": signature.to_dict(),
            "signature_1": mn_signatures[0].to_dict(),
            "signature_2": mn_signatures[1].to_dict(),
            "signature_3": mn_signatures[2].to_dict(),
        })

        # make sure we validate correctly
        final_ticket.validate(self.__chainwrapper)
        return final_ticket

    def __collect_mn_regticket_signatures(self, signature, ticket, masternode_ordering):
        signatures = []
        for mn_pub in masternode_ordering:
            mn = self.__chainwrapper.get_masternode(mn_pub)
            data_from_mn = mn.masternode_sign_registration_ticket(signature.serialize(), ticket.serialize())

            # client parses signed ticket and validated signature
            mn_signature = Signature(serialized=data_from_mn)

            # is the data the same and the signature valid?
            require_true(mn_signature.pubkey == mn_pub)
            mn_signature.validate(ticket)

            # add signature to collected signatures
            signatures.append(mn_signature)
        return signatures

    def __collect_mn_actticket_signatures(self, signature, ticket, image, masternode_ordering):
        # TODO: refactor the two MN signature collection functions into one
        signatures = []
        for mn_pub in masternode_ordering:
            mn = self.__chainwrapper.get_masternode(mn_pub)
            data_from_mn = mn.masternode_sign_activation_ticket(signature.serialize(), ticket.serialize(),
                                                                image.serialize())

            # client parses signed ticket and validated signature
            mn_signature = Signature(serialized=data_from_mn)

            # is the data the same and the signature valid?
            require_true(mn_signature.pubkey == mn_pub)
            mn_signature.validate(ticket)

            # add signature to collected signatures
            signatures.append(mn_signature)
        return signatures

    def __rpc_mn_store_ticket(self, ticket, mn_pubkey, tickettype):
        mn = self.__chainwrapper.get_masternode(mn_pubkey)
        return mn.masternode_place_ticket_on_blockchain(ticket, tickettype=tickettype)

    def __rpc_mn_store_image(self, regticket_txid, image, mn_pubkey):
        mn = self.__chainwrapper.get_masternode(mn_pubkey)
        mn.masternode_place_image_data_in_chunkstorage(regticket_txid, image.serialize())

    def __wait_for_ticket_on_blockchain(self, regticket_txid):
        serialized = self.__blockchain.retrieve_data_from_utxo(regticket_txid)
        new_ticket = FinalRegistrationTicket(serialized=serialized)

        # validate new ticket
        new_ticket.validate(self.__chainwrapper)
        return new_ticket

    def register_image(self, image_data, artist_name=None, artist_website=None, artist_written_statement=None,
                       artwork_title=None, artwork_series_name=None, artwork_creation_video_youtube_url=None,
                       artwork_keyword_set=None, total_copies=None):
        # generate image ticket

        image = ImageData(dictionary={
            "image": image_data,
            "lubychunks": ImageData.generate_luby_chunks(image_data),
            "thumbnail": ImageData.generate_thumbnail(image_data),
        })
        image.validate()

        # generate registration ticket
        regticket = RegistrationTicket(dictionary={
            "artist_name": artist_name,
            "artist_website": artist_website,
            "artist_written_statement": artist_written_statement,

            "artwork_title": artwork_title,
            "artwork_series_name": artwork_series_name,
            "artwork_creation_video_youtube_url": artwork_creation_video_youtube_url,
            "artwork_keyword_set": artwork_keyword_set,
            "total_copies": total_copies,

            "fingerprints": image.generate_fingerprints(),
            "lubyhashes": image.get_luby_hashes(),
            "lubyseeds": image.get_luby_seeds(),
            "thumbnailhash": image.get_thumbnail_hash(),

            "author": self.__pubkey,
            "order_block_txid": self.__chainwrapper.get_last_block_hash(),
            "imagedata_hash": image.get_artwork_hash(),
        })

        # make sure we validate correctly
        regticket.validate(self.__chainwrapper)

        # get masternode ordering from regticket
        masternode_ordering = self.__chainwrapper.get_masternode_order(regticket.order_block_txid)

        # sign ticket
        signature_regticket = self.__generate_signed_ticket(regticket)

        # have masternodes sign the ticket
        mn_signatures = self.__collect_mn_regticket_signatures(signature_regticket, regticket, masternode_ordering)

        # assemble final regticket
        final_regticket = self.__generate_final_ticket(FinalRegistrationTicket, regticket, signature_regticket,
                                                       mn_signatures)

        # ask first MN to store regticket on chain
        regticket_txid = self.__rpc_mn_store_ticket(final_regticket, masternode_ordering[0], tickettype="regticket")

        # wait for regticket to show up on the chain
        self.__wait_for_ticket_on_blockchain(regticket_txid)

        # generate activation ticket
        actticket = ActivationTicket(dictionary={
            "author": self.__pubkey,
            "order_block_txid": regticket.order_block_txid,
            "registration_ticket_txid": regticket_txid,
        })
        actticket.validate(self.__chainwrapper, image)

        # sign actticket
        signature_actticket = self.__generate_signed_ticket(actticket)

        # place image in chunkstorage
        self.__rpc_mn_store_image(regticket_txid, image, masternode_ordering[0])

        # have masternodes sign the ticket
        mn_signatures = self.__collect_mn_actticket_signatures(signature_actticket, actticket, image,
                                                               masternode_ordering)

        # create combined activation ticket
        final_actticket = self.__generate_final_ticket(FinalActivationTicket, actticket, signature_actticket,
                                                       mn_signatures)

        # ask first MN to store regticket on chain
        actticket_txid = self.__rpc_mn_store_ticket(final_actticket, masternode_ordering[0], tickettype="actticket")

        return actticket_txid


class IDRegistrationClient:
    def __init__(self, privkey, pubkey, chainwrapper):
        self.__privkey = privkey
        self.__pubkey = pubkey
        self.__chainwrapper = chainwrapper

    def register_id(self, address):
        idticket = IDTicket(dictionary={
            "blockchain_address": address,
            "public_key": self.__pubkey,
            "ticket_submission_time": int(time.time()),
        })
        idticket.validate()

        signature = Signature(dictionary={
            "signature": pastel_id_write_signature_on_data_func(idticket.serialize(), self.__privkey, self.__pubkey),
            "pubkey": self.__pubkey,
        })
        signature.validate(idticket)

        finalticket = FinalIDTicket(dictionary={
            "ticket": idticket.to_dict(),
            "signature": signature.to_dict(),
        })
        finalticket.validate()

        self.__chainwrapper.store_ticket(finalticket)
