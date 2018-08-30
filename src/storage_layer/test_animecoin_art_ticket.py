import sys
import json

from pprint import pprint

from dht_prototype.masternode_modules.animecoin_modules.animecoin_signatures import\
    animecoin_id_write_signature_on_data_func, animecoin_id_verify_signature_with_public_key_func
from dht_prototype.masternode_modules.animecoin_modules.animecoin_keys import animecoin_id_keypair_generation_func
from dht_prototype.masternode_modules.models_new import ImageData, RegistrationTicket, ActivationTicket, \
    Signature, FinalRegistrationTicket
from dht_prototype.masternode_modules.mockchain import BlockChain
from dht_prototype.masternode_modules.masternode_ticketing import masternode_verify_registration_ticket,\
    masternode_place_registration_ticket


if __name__ == "__main__":
    # parse parameters and generate stuff
    fingerprint_file = sys.argv[1]
    image_file = sys.argv[2]
    # TODO: transition from base64 to binary keys to save space
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

    # create registration ticket
    regticket = RegistrationTicket(dictionary={
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

        "author": pubkey,
        "imagedata_hash": image.get_artwork_hash(),
    })
    regticket_serialized = regticket.serialize()

    signature_regticket = Signature(dictionary={
        "signature": animecoin_id_write_signature_on_data_func(regticket_serialized, privkey, pubkey),
        "pubkey": pubkey,
    })

    # make sure we validate correctly
    signature_regticket.validate(regticket)

    # ask MNs to sign
    mn_signatures = []
    for mn_pub in masternode_ordering:
        mn_priv = masternodes[mn_pub]
        data_from_mn = masternode_verify_registration_ticket(signature_regticket.serialize(), regticket_serialized,
                                                             blockchain, mn_pub, mn_priv)

        # client parses signed ticket and validated signature
        mn_signature = Signature(serialized=data_from_mn)

        # is the data the same and the signature valid?
        assert(mn_signature.pubkey == mn_pub)
        mn_signature.validate(regticket)

        # add signature to collected signatures
        mn_signatures.append(mn_signature)

    # create combined registration ticket
    final_regticket = FinalRegistrationTicket(dictionary={
        "registration_ticket": regticket.to_dict(),
        "signature_author": signature_regticket.to_dict(),
        "signature_1": mn_signatures[0].to_dict(),
        "signature_2": mn_signatures[1].to_dict(),
        "signature_3": mn_signatures[2].to_dict(),
    })
    final_regticket.validate(masternode_ordering, blockchain)
    assert (final_regticket == FinalRegistrationTicket(serialized=final_regticket.serialize()))
    pprint(final_regticket.to_dict())
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
    })
