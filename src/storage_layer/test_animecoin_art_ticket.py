import sys
import json

from pprint import pprint

from dht_prototype.masternode_modules.animecoin_modules.animecoin_signatures import\
    animecoin_id_write_signature_on_data_func, animecoin_id_verify_signature_with_public_key_func
from dht_prototype.masternode_modules.animecoin_modules.animecoin_keys import animecoin_id_keypair_generation_func
from dht_prototype.masternode_modules.models_new import ImageData, RegistrationTicket, ActivationTicket, \
    Signature, FinalRegistrationTicket, FinalActivationTicket
from dht_prototype.masternode_modules.mockchain import BlockChain, ChainWrapper
from dht_prototype.masternode_modules.mockstorage import ChunkStorage
from dht_prototype.masternode_modules.masternode_ticketing import RegistrationServer


class RegistrationClient:
    def __init__(self, privkey, pubkey, blockchain, chunkstorage):
        self.__blockchain = blockchain
        self.__chainwrapper = ChainWrapper(blockchain)
        self.__chunkstorage = chunkstorage

        # get MN ordering
        self.__privkey = privkey
        self.__pubkey = pubkey

    def __generate_signed_ticket(self, ticket):
        signed_ticket = Signature(dictionary={
            "signature": animecoin_id_write_signature_on_data_func(ticket.serialize(), self.__privkey, self.__pubkey),
            "pubkey": pubkey,
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
            assert (mn_signature.pubkey == mn_pub)
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
            assert (mn_signature.pubkey == mn_pub)
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

    def register_image(self, image_file, artist_name=None, artist_website=None, artist_written_statement=None,
                             artwork_title=None, artwork_series_name=None, artwork_creation_video_youtube_url=None,
                             artwork_keyword_set=None, total_copies=None):
        # generate image ticket
        imagedata = open(image_file, "rb").read()
        image = ImageData(dictionary={
            "image": imagedata,
            "lubychunks": ImageData.generate_luby_chunks(imagedata),
            "thumbnail": ImageData.generate_thumbnail(imagedata),
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

            "author": pubkey,
            "order_block_txid": self.__chainwrapper.get_last_block_hash(),
            "imagedata_hash": image.get_artwork_hash(),
        })

        # make sure we validate correctly
        regticket.validate(self.__chainwrapper)

        # get masternode ordering from regticket
        masternode_ordering = chainwrapper.get_masternode_order(regticket.order_block_txid)

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


def get_ticket_as_new_node(actticket_txid, chainwrapper, chunkstorage):
    # find final activation ticket and validate signatures
    final_actticket_serialized = chainwrapper.retrieve_ticket(actticket_txid)
    print("FINAL ACT TICKET SERIALIZED SIZE:", len(final_actticket_serialized))
    final_actticket = FinalActivationTicket(serialized=final_actticket_serialized)

    # validate signatures by MNs
    final_actticket.validate(chainwrapper)

    # get final registration ticket
    final_regticket_serialized = chainwrapper.retrieve_ticket(final_actticket.ticket.registration_ticket_txid)
    print("FINAL REGTICKET SERIALIZED SIZE:", len(final_regticket_serialized))
    final_regticket = FinalRegistrationTicket(serialized=final_regticket_serialized)

    # validate signatures by MNs
    final_regticket.validate(chainwrapper)

    # get registration ticket
    regticket = final_regticket.ticket

    print("#"*200)
    print("Regticket received from chain:")
    print("author", regticket.author)
    print("artwork_title", regticket.artwork_title)
    print("thumbnailhash", regticket.thumbnailhash)
    print("imagedata_hash", regticket.imagedata_hash)

    thumbnail = chunkstorage.get(regticket.thumbnailhash)
    print("Fetched thumbnail:", len(thumbnail))
    print("Thumbnail:", len(thumbnail))
    print("#" * 200)


if __name__ == "__main__":
    # parse parameters and generate stuff
    fingerprint_file = sys.argv[1]
    image_files = sys.argv[2:]

    # TODO: transition from base64 to binary keys to save space
    privkey, pubkey = animecoin_id_keypair_generation_func()

    # START MOCK STUFF
    # TODO: remove mock stuff
    # our mockchain and mockstorage
    blockchain = BlockChain()
    chainwrapper = ChainWrapper(blockchain)
    chunkstorage = ChunkStorage()

    # TODO: remove mock stuff
    # register mock artist
    chainwrapper.store_ticket(tickettype="artist", data=pubkey)

    # TODO: remove mock stuff
    # register mock MNs
    masternodes = []
    for i in range(10):
        masternode = RegistrationServer(blockchain, chunkstorage)
        masternodes.append(masternode)
    # END MOCK STUFF

    # get the selfistration object
    artreg = RegistrationClient(privkey, pubkey, blockchain, chunkstorage)

    for image_file in image_files:
        print("Registering image: %s" % image_file)

        # register image
        actticket_txid = artreg.register_image(
            image_file=image_file,
            artist_name="Example Artist",
            artist_website="exampleartist.com",
            artist_written_statement="This is only a test",
            artwork_title="My Example Art",
            artwork_series_name="Examples and Tests collection",
            artwork_creation_video_youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            artwork_keyword_set="example, testing, sample",
            total_copies=10
        )

        # get and process ticket as new node
        get_ticket_as_new_node(actticket_txid, chainwrapper, chunkstorage)
