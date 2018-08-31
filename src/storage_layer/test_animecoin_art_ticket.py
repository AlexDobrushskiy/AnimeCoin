import sys
import json

from pprint import pprint

from dht_prototype.masternode_modules.animecoin_modules.animecoin_signatures import\
    animecoin_id_write_signature_on_data_func, animecoin_id_verify_signature_with_public_key_func
from dht_prototype.masternode_modules.animecoin_modules.animecoin_keys import animecoin_id_keypair_generation_func
from dht_prototype.masternode_modules.models_new import ImageData, RegistrationTicket, ActivationTicket, \
    Signature, FinalRegistrationTicket, FinalActivationTicket
from dht_prototype.masternode_modules.mockchain import BlockChain
from dht_prototype.masternode_modules.mockstorage import ChunkStorage
from dht_prototype.masternode_modules.masternode_ticketing import RegistrationServer


class RegistrationClient:
    def __init__(self, privkey, pubkey, blockchain, chunkstorage, masternode_ordering):
        self.__blockchain = blockchain
        self.__chunkstorage = chunkstorage

        # get MN ordering
        self.__privkey = privkey
        self.__pubkey = pubkey
        self.__masternode_ordering = masternode_ordering

    def generate_image_ticket(self, filename):
        imagedata = open(filename, "rb").read()

        # create image ticket
        image = ImageData(dictionary={
            "image": imagedata,
            "lubychunks": ImageData.generate_luby_chunks(imagedata),
            "thumbnail": ImageData.generate_thumbnail(imagedata),
        })
        image.validate()
        return image

    def generate_registration_ticket(self, image, artist_name=None, artist_website=None, artist_written_statement=None,
                                     artwork_title=None, artwork_series_name=None, artwork_creation_video_youtube_url=None,
                                     artwork_keyword_set=None, total_copies=None):

        # create registration ticket
        regticket = RegistrationTicket(dictionary={
            "artist_name": artist_name,
            "artist_website": artist_website,
            "artist_written_statement": artist_written_statement,

            "artwork_title": artwork_title,
            "artwork_series_name": artwork_series_name,
            "artwork_creation_video_youtube_url": artwork_creation_video_youtube_url,
            "artwork_keyword_set": artwork_keyword_set,
            "total_copies": total_copies,

            "fingerprints": image.generate_fingerprints(image),
            "lubyhashes": image.get_luby_hashes(),
            "thumbnailhash": image.get_thumbnail_hash(),

            "author": pubkey,
            "imagedata_hash": image.get_artwork_hash(),
        })

        # make sure we validate correctly
        regticket.validate(self.__blockchain)
        return regticket

    def generate_activation_ticket(self, regticket_txid, image):
        actticket = ActivationTicket(dictionary={
            "author": self.__pubkey,
            "registration_ticket_txid": regticket_txid,
        })
        actticket.validate(self.__masternode_ordering, self.__blockchain, image)
        return actticket

    def generate_signed_ticket(self, ticket):
        signed_ticket = Signature(dictionary={
            "signature": animecoin_id_write_signature_on_data_func(ticket.serialize(), self.__privkey, self.__pubkey),
            "pubkey": pubkey,
        })

        # make sure we validate correctly
        signed_ticket.validate(ticket)
        return signed_ticket

    def generate_final_ticket(self, cls, ticket, signature, mn_signatures):
        # create combined registration ticket
        final_ticket = cls(dictionary={
            "ticket": ticket.to_dict(),
            "signature_author": signature.to_dict(),
            "signature_1": mn_signatures[0].to_dict(),
            "signature_2": mn_signatures[1].to_dict(),
            "signature_3": mn_signatures[2].to_dict(),
        })

        # make sure we validate correctly
        final_ticket.validate(self.__masternode_ordering, self.__blockchain)
        return final_ticket

    def collect_mn_regticket_signatures(self, signature, ticket):
        signatures = []
        for mn_pub in self.__masternode_ordering:
            mn = self.__blockchain.get_masternode(mn_pub)
            data_from_mn = mn.masternode_sign_registration_ticket(signature.serialize(), ticket.serialize())

            # client parses signed ticket and validated signature
            mn_signature = Signature(serialized=data_from_mn)

            # is the data the same and the signature valid?
            assert (mn_signature.pubkey == mn_pub)
            mn_signature.validate(ticket)

            # add signature to collected signatures
            signatures.append(mn_signature)
        return signatures

    def collect_mn_actticket_signatures(self, signature, ticket, image):
        # TODO: refactor the two MN signature collection functions into one
        signatures = []
        for mn_pub in self.__masternode_ordering:
            mn = self.__blockchain.get_masternode(mn_pub)
            data_from_mn = mn.masternode_sign_activation_ticket(signature.serialize(), ticket.serialize(),
                                                                image.serialize(), self.__masternode_ordering)

            # client parses signed ticket and validated signature
            mn_signature = Signature(serialized=data_from_mn)

            # is the data the same and the signature valid?
            assert (mn_signature.pubkey == mn_pub)
            mn_signature.validate(actticket)

            # add signature to collected signatures
            signatures.append(mn_signature)
        return signatures

    def rpc_mn_store_ticket(self, ticket):
        mn = self.__blockchain.get_masternode(self.__masternode_ordering[0])
        return mn.masternode_place_ticket_on_blockchain(ticket, self.__masternode_ordering)

    def rpc_mn_store_image(self, image):
        mn = self.__blockchain.get_masternode(self.__masternode_ordering[0])
        mn.masternode_place_image_data_in_chunkstorage(image.serialize())

    def wait_for_ticket_on_blockchain(self, regticket_txid):
        serialized = self.__blockchain.retrieve_data_from_utxo(regticket_txid)
        new_ticket = FinalRegistrationTicket(serialized=serialized)

        # validate new ticket
        new_ticket.validate(self.__masternode_ordering, self.__blockchain)
        return new_ticket


def get_ticket_as_new_node(actticket_txid, blockchain, chunkstorage):
    # find final activation ticket and validate signatures
    final_actticket_serialized = blockchain.retrieve_data_from_utxo(actticket_txid)
    final_actticket = FinalActivationTicket(serialized=final_actticket_serialized)

    # validate signatures by MNs
    final_actticket.validate(masternode_ordering, blockchain)

    # get final registration ticket
    final_regticket_serialized = blockchain.retrieve_data_from_utxo(final_actticket.ticket.registration_ticket_txid)
    final_regticket = FinalRegistrationTicket(serialized=final_regticket_serialized)

    # validate signatures by MNs
    final_regticket.validate(masternode_ordering, blockchain)

    # get registration ticket
    regticket = final_regticket.ticket

    print("Regticket received from chain:")
    print("author", regticket.author)
    print("artwork_title", regticket.artwork_title)
    print("lubyhashes", regticket.lubyhashes)
    print("thumbnailhash", regticket.thumbnailhash)
    print("imagedata_hash", regticket.imagedata_hash)

    thumbnail = chunkstorage.get(regticket.thumbnailhash)
    print("Fetched thumbnail:", len(thumbnail))
    print("Thumbnail:", thumbnail)


if __name__ == "__main__":
    # parse parameters and generate stuff
    fingerprint_file = sys.argv[1]
    image_file = sys.argv[2]

    # TODO: transition from base64 to binary keys to save space
    privkey, pubkey = animecoin_id_keypair_generation_func()
    # TODO: mock fingerprints
    fingerprint_floats = json.load(open(fingerprint_file))

    # START MOCK STUFF
    # TODO: remove mock stuff
    # our mockchain and mockstorage
    blockchain = BlockChain()
    chunkstorage = ChunkStorage()

    # TODO: remove mock stuff
    # register mock artist
    blockchain.register_pubkey(pubkey)

    # TODO: remove mock stuff
    # register mock MNs
    masternodes = []
    for i in range(3):
        masternode = RegistrationServer(blockchain, chunkstorage)
        masternodes.append(masternode)

    masternode_ordering = blockchain.get_top_n_masternodes(3)
    # END MOCK STUFF

    # get the artregistration object
    artreg = RegistrationClient(privkey, pubkey, blockchain, chunkstorage, masternode_ordering)

    # generate image ticket
    image = artreg.generate_image_ticket(image_file)

    # generate registration ticket
    regticket = artreg.generate_registration_ticket(
        image,
        artist_name="Example Artist",
        artist_website="exampleartist.com",
        artist_written_statement="This is only a test",
        artwork_title="My Example Art",
        artwork_series_name="Examples and Tests collection",
        artwork_creation_video_youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        artwork_keyword_set="example, testing, sample",
        total_copies=10
    )

    # sign ticket
    signature_regticket = artreg.generate_signed_ticket(regticket)

    # have masternodes sign the ticket
    mn_signatures = artreg.collect_mn_regticket_signatures(signature_regticket, regticket)

    # assemble final regticket
    final_regticket = artreg.generate_final_ticket(FinalRegistrationTicket, regticket, signature_regticket, mn_signatures)

    # ask first MN to store regticket on chain
    regticket_txid = artreg.rpc_mn_store_ticket(final_regticket)

    # wait for regticket to show up on the chain
    new_regticket = artreg.wait_for_ticket_on_blockchain(regticket_txid)

    # generate activation ticket
    actticket = artreg.generate_activation_ticket(regticket_txid, image)

    # sign actticket
    signature_actticket = artreg.generate_signed_ticket(actticket)

    # place image in chunkstorage
    artreg.rpc_mn_store_image(image)

    # have masternodes sign the ticket
    mn_signatures = artreg.collect_mn_actticket_signatures(signature_actticket, actticket, image)

    # create combined activation ticket
    final_actticket = artreg.generate_final_ticket(FinalActivationTicket, actticket, signature_actticket, mn_signatures)

    # ask first MN to store regticket on chain
    actticket_txid = artreg.rpc_mn_store_ticket(final_actticket)

    # get and process ticket as new node
    get_ticket_as_new_node(actticket_txid, blockchain, chunkstorage)
