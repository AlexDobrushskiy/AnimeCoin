import sys
import json
import base64

# from dht_prototype.masternode_modules.models import ArtTicket
from dht_prototype.masternode_modules.animecoin_modules.animecoin_compression import compress

from dht_prototype.masternode_modules.helpers import get_digest as get_sha2_256_digest
from dht_prototype.masternode_modules.animecoin_modules.animecoin_keys import animecoin_id_keypair_generation_func
from dht_prototype.masternode_modules.models_new import MetaData, ImageData, RegistrationTicket, ActivationTicket


class MockChain:
    def __init__(self):
        pass

    def get_artist_user_id(self, pubkey):
        raise NotImplementedError()

    def get_all_fingerprints(self):
        # TODO: get all fingerprints for registered art and stuff in mempool
        raise NotImplementedError()

    def art_hash_not_on_chain_or_mempool(self, art_hash):
        raise NotImplementedError()


if __name__ == "__main__":
    # ticket = ArtTicket()
    # d = ticket.to_dict()
    #
    # data = json.dumps(d)
    # print("Original size: %s" % len(data))
    #
    # samples = [data.encode("utf-8")]
    # cdict = zstd.train_dictionary(256, samples)
    #
    # compressed = compress(data)
    # print("compressed without dict: %s" % len(compressed))
    #
    # compressed = compress(data, compressiondict=zstd.train_dictionary(256, samples))
    # print("compressed with dict: %s" % len(compressed))

    # parse parameters and generate stuff
    fingerprint_file = sys.argv[1]
    image_file = sys.argv[2]
    privkey, pubkey = animecoin_id_keypair_generation_func()
    fingerprint_floats = json.load(open(fingerprint_file))

    # our mockchain
    blockchain = MockChain()

    # create image
    imagedata = open(image_file, "rb").read()
    image = ImageData(dictionary={
        "image": {"ARTWORK": imagedata},
        "lubychunks": ImageData.generate_luby_chunks(imagedata),
        "thumbnail": ImageData.generate_thumbnail(imagedata),
    })
    image.validate()

    # create metadata
    metadata = MetaData(dictionary={
        "artistinfo": {
            "ARTIST_USERID": blockchain.get_artist_user_id(base64.b64decode(pubkey)),
            "ARTIST_NAME": "Example Artist",
            "ARTIST_WEBSITE": "https://example.com",
            "ARTIST_WRITTEN_STATEMENT": "This is an example artwork",
        },
        "artinfo": {
            "ARTWORK_TITLE": "Example Artwork",
            "ARTWORK_SERIES_NAME": "Example Series",
            "ARTWORK_CREATION_VIDEO_YOUTUBE_URL": "https://www.youtube.com/watch?v=exampleid",
            "ARTWORK_KEYWORD_SET": "example, test, artwork, firsttransaction",
            "TOTAL_COPIES": 10,
        },
        "fingerprints": {
            # "FINGERPRINTS": ImageData.generate_fingerprints(image)
            # TODO: get rid of the faux fingerprint
            "FINGERPRINTS": fingerprint_floats,
        },
        "lubyhashes": {
            "LUBY_CHUNK_HASHES": image.lubychunks.get_hashes()
        },
        "thumbnailhash": {
            "HASH": image.thumbnail.get_hash()
        }
    })
    # TODO: this needs to be decided
    # metadata.validate()

    # tmp
    assert(metadata == MetaData(serialized=metadata.serialize()))

    # create registration ticket
    regticket = RegistrationTicket(dictionary={
        "imagedata_hash": {
            "HASH": image.get_artwork_hash()
        },
        "metadata_hash": {
            "HASH": metadata.get_hash()
        },
    })

    actticket = ActivationTicket(dictionary={
        "registration_ticket_txid": {
            # TODO: get this from the blockchain - ticket hash is sha2 256!
            "TXID": get_sha2_256_digest(regticket.serialize())
        },
        "metadata_hash": {
            "HASH": metadata.get_hash()
        }
    })
