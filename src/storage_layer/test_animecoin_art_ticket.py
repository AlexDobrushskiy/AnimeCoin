import sys
import json

from pprint import pprint

from dht_prototype.masternode_modules.animecoin_modules.animecoin_signatures import\
    animecoin_id_write_signature_on_data_func, animecoin_id_verify_signature_with_public_key_func
from dht_prototype.masternode_modules.animecoin_modules.animecoin_keys import animecoin_id_keypair_generation_func
from dht_prototype.masternode_modules.models_new import MetaData, ImageData, RegistrationTicket, ActivationTicket, \
    Signature, FinalRegistrationTicket
from dht_prototype.masternode_modules.mockchain import BlockChain
from dht_prototype.masternode_modules.masternode_ticketing import masternode_verify_registration_ticket,\
    masternode_place_registration_ticket


if __name__ == "__main__":
    # parse parameters and generate stuff
    fingerprint_file = sys.argv[1]
    image_file = sys.argv[2]
    privkey, pubkey = animecoin_id_keypair_generation_func()
    fingerprint_floats = json.load(open(fingerprint_file))

    # our mockchain
    blockchain = BlockChain()

    # register mock artist
    blockchain.register_pubkey(pubkey)

    # register mock MNs
    masternodes = {}
    for i in range(3):
        tmp_priv, tmp_pub = animecoin_id_keypair_generation_func()
        blockchain.register_pubkey(tmp_pub)
        blockchain.register_masternode(tmp_pub, tmp_pub)
        masternodes[tmp_pub] = tmp_priv

    # get MN ordering
    masternode_ordering = blockchain.get_top_n_masternodes(3)

    # create image
    imagedata = open(image_file, "rb").read()
    image = ImageData(dictionary={
        "image": imagedata,
        "lubychunks": ImageData.generate_luby_chunks(imagedata),
        "thumbnail": ImageData.generate_thumbnail(imagedata),
    })
    image.validate()

    # create metadata
    metadata = MetaData(dictionary={
        "artist_userid": blockchain.get_id_for_pubkey(pubkey),
        "artist_name": "Example Artist",
        "artist_website": "https://example.com",
        "artist_written_statement": "This is an example artwork",

        "artwork_title": "Example Artwork",
        "artwork_series_name": "Example Series",
        "artwork_creation_video_youtube_url": "https://www.youtube.com/watch?v=exampleid",
        "artwork_keyword_set": "example, test, artwork, firsttransaction",
        "total_copies": 10,

        "fingerprints": image.generate_fingerprints(image),
        "lubyhashes": image.get_luby_hashes(),
        "thumbnailhash": image.get_thumbnail_hash(),
    })

    # see if we do indeed validate
    metadata.validate(image)

    # tmp
    metadata_serialized = metadata.serialize()
    assert(metadata == MetaData(serialized=metadata_serialized))

    # create registration ticket
    regticket = RegistrationTicket(dictionary={
        "author": pubkey,
        "imagedata_hash": image.get_artwork_hash(),
        "metadata_hash": metadata.get_hash(),
    })
    regticket_serialized = regticket.serialize()

    signature_regticket = Signature(dictionary={
        "signature": animecoin_id_write_signature_on_data_func(regticket_serialized, privkey, pubkey),
        "pubkey": pubkey,
    })

    # make sure we validate correctly
    signature_regticket.validate(regticket.serialize())

    # ask MNs to sign
    mn_signatures = []
    for mn_pub in masternode_ordering:
        mn_priv = masternodes[mn_pub]
        data_from_mn = masternode_verify_registration_ticket(signature_regticket.serialize(), regticket_serialized,
                                                             metadata.serialize(), blockchain, mn_pub, mn_priv)

        # client parses signed ticket and validated signature
        mn_signature = Signature(serialized=data_from_mn)

        # is the data the same and the signature valid?
        assert(mn_signature.pubkey == mn_pub)
        mn_signature.validate(regticket_serialized)

        # add signature to collected signatures
        mn_signatures.append(mn_signature)

    # create combined registration ticket
    final_regticket = FinalRegistrationTicket(dictionary={
        "metadata": metadata_serialized,
        "registration_ticket": regticket_serialized,
        "signature_author": signature_regticket.serialize(),
        "signature_1": mn_signatures[0].serialize(),
        "signature_2": mn_signatures[1].serialize(),
        "signature_3": mn_signatures[2].serialize(),
    })
    final_regticket.validate(masternode_ordering, blockchain)
    assert (final_regticket == FinalRegistrationTicket(serialized=final_regticket))
    exit()

    # ask first MN to store regticket on chain
    regticket_txid = masternode_place_registration_ticket(signature_regticket, mn_pub, mn_priv, blockchain,
                                                          masternode_ordering)
    exit()

    # wait for regticket to show up on the chain
    regticket = blockchain.retrieve_data_from_utxo(regticket_txid)

    actticket = ActivationTicket(dictionary={
        # TODO: get this from the blockchain - ticket hash is sha2 256!
        "registration_ticket_txid": regticket_txid,
        "metadata_hash": metadata.get_hash(),
    })
