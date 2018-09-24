import sys


from dht_prototype.masternode_modules.animecoin_modules.animecoin_keys import animecoin_id_keypair_generation_func
from dht_prototype.masternode_modules.ticket_models import FinalRegistrationTicket, FinalActivationTicket
from dht_prototype.masternode_modules.blockchain_wrapper import MockChain, ChainWrapper
from dht_prototype.masternode_modules.mockstorage import ChunkStorage
from dht_prototype.masternode_modules.masternode_ticketing import ArtRegistrationServer, ArtRegistrationClient


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
    image_files = sys.argv[1:]

    # TODO: transition from base64 to binary keys to save space
    privkey, pubkey = animecoin_id_keypair_generation_func()

    # START MOCK STUFF
    # TODO: remove mock stuff
    # our mockchain and mockstorage
    blockchain = MockChain()
    chainwrapper = ChainWrapper(blockchain)
    chunkstorage = ChunkStorage()

    # TODO: remove mock stuff
    # register mock artist
    # TODO: implement this properly
    # chainwrapper.store_ticket(tickettype="artist", data=pubkey)

    # TODO: remove mock stuff
    # register mock MNs
    masternodes = []
    for i in range(10):
        masternode = ArtRegistrationServer(blockchain, chunkstorage)
        masternodes.append(masternode)
    # END MOCK STUFF

    # get the selfistration object
    artreg = ArtRegistrationClient(privkey, pubkey, blockchain)

    for image_file in image_files:
        print("Registering image: %s" % image_file)

        # register image
        image_data = open(image_file, "rb").read()
        actticket_txid = artreg.register_image(
            image_data=image_data,
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
