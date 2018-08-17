import sys
import base64
import zstd

# TODO: do we want to use sha3_512 for this?
from dht_prototype.masternode_modules.animecoin_modules.helpers import get_sha3_512_func_bytes
from dht_prototype.masternode_modules.animecoin_modules.animecoin_signatures import animecoin_id_write_signature_on_data_func, animecoin_id_verify_signature_with_public_key_func
from dht_prototype.masternode_modules.animecoin_modules.animecoin_keys import animecoin_id_keypair_generation_func
from dht_prototype.masternode_modules.models import ArtRegistrationRequest, load_artregistration_ticket,\
    serialize_artregistration_ticket, serialize_signatures, load_signatures
from dht_prototype.masternode_modules.model_validators import ARTREGISTRATION_KEYS
from dht_prototype.masternode_modules.animecoin_modules.animecoin_compression import compress, decompress

# step 1
# X artist constructs reg ticket
# X sign ticket
# X for every MN:
#   X MN validates signature
#   X MN validates hash
#   X MN validates ticket
#   X if all is well, MN signs
# o make sure validator works right
#   o validate thumbnail
#   o validate metadata
#   o validate
# X blockchain verifies ticket with all signatures

# step 2
# o artist constructs verification ticket
# o sign ticket
# o for every MN:
#   o validate signature
#   o validate hash
#   o validate that activation ticket belongs to registration ticket
#   o validate that registration ticket has not been activated yet
#   o validate that image is the one in registration ticket
#   o generate and verify fingerprints from registration ticket
#   o generate and verify thumbnail from registration ticket
#   o run nsfw detection
#   o run dupe detection
#   o sign


def get_fingerprint(image_file):
    # TODO:
    return "DUMMY FINGERPRINT"


def create_registration_ticket(image_file, pubkey):
    # 1) Artist fills registration ticket

    datadict = {
        "ARTIST_PUBKEY": base64.b64decode(pubkey),
        "ARTWORK_TITLE": "Example Title",
        "ARTIST_NAME": "Example Artist",
        "ARTWORK_SERIES_NAME": "Example Series",
        "ARTWORK_CREATION_VIDEO_YOUTUBE_URL": "https://www.youtube.com/watch?v=exampleid",
        "ARTIST_WEBSITE": "https://example.com",
        "ARTIST_WRITTEN_STATEMENT": "This is an example artwork",
        "ARTWORK_KEYWORD_SET": "example, test, artwork, firsttransaction",
        "TOTAL_COPIES": 10,
        "IMAGE_HASH": get_sha3_512_func_bytes(image_file),
        "IMAGE_FINGERPRINT_HASH": get_sha3_512_func_bytes(get_fingerprint(image_file)),
    }
    ticket = ArtRegistrationRequest(datadict)

    # serialize and sign ticket
    serialized_data = serialize_artregistration_ticket(ticket)
    serialized_hash = get_sha3_512_func_bytes(serialized_data)
    return serialized_data, serialized_hash


def client_sign_registration_ticket(serialized_hash, privkey, pubkey):
    return animecoin_id_write_signature_on_data_func(serialized_hash, privkey, pubkey)


# TODO: perhaps move this to into the proper validator?
def __validate_data(serialized_data, serialized_hash):
    # validate hash
    if serialized_hash != get_sha3_512_func_bytes(serialized_data):
        raise ValueError("Hash does not match!")

    # unpack and validate data
    ticket = ArtRegistrationRequest(load_artregistration_ticket(serialized_data))

    # validate signature on data
    pubkey = base64.b64encode(ticket.ARTIST_PUBKEY)
    if not animecoin_id_verify_signature_with_public_key_func(serialized_hash, client_signature, pubkey):
        raise ValueError("Validation failed!")


def masternode_sign_registration_ticket(serialized_data, serialized_hash, client_signature, mn_privkey, mn_pubkey):
    __validate_data(serialized_data, serialized_hash)

    # all is well, sign the ticket
    return animecoin_id_write_signature_on_data_func(serialized_hash, mn_privkey, mn_pubkey)


def blockchain_verify_ticket(serialized_data, serialized_hash, signatures):
    __validate_data(serialized_data, serialized_hash)

    for pubkey, signature in signatures:
        if not animecoin_id_verify_signature_with_public_key_func(serialized_hash, signature, pubkey):
            raise ValueError("Validation failed for signature: %s" % signature)


if __name__ == "__main__":
    image_file = open(sys.argv[1], "rb").read()
    privkey, pubkey = animecoin_id_keypair_generation_func()
    masternodes = []
    for i in range(3):
        masternodes.append((animecoin_id_keypair_generation_func()))

    ### STEP 1 ###
    # create ticket
    serialized_data, serialized_hash = create_registration_ticket(image_file, pubkey)
    print("Serialized data:", serialized_data)
    print("Ticket created, len:", len(serialized_data))

    # compress ticket
    samples = list([x.encode("utf-8") for x in ARTREGISTRATION_KEYS.keys()])
    print(samples)
    compressiondict = zstd.train_dictionary(256, samples)
    compressed_ticket = compress(serialized_data, compressiondict=compressiondict)
    print("Compressed:", len(compressed_ticket))

    # sign ticket
    client_signature = client_sign_registration_ticket(serialized_hash, privkey, pubkey)

    # have MNs validate and sign ticket
    signatures = [(pubkey, client_signature)]
    for mn_privkey, mn_pubkey in masternodes:
        mn_signature = masternode_sign_registration_ticket(serialized_data, serialized_hash, client_signature, mn_privkey, mn_pubkey)
        signatures.append((mn_pubkey, mn_signature))

    # submit to blockchain -> verify all signatures
    blockchain_verify_ticket(serialized_data, serialized_hash, signatures)
    print("Ticket validated!")

    # now we have:
    # o serialized_data -> msgpack()ed ticket
    # o serialized_hash -> hash of data
    # o signatures -> [clientsig, MN1sig, MN2sig, MN3sig]

    print("Signatures:", signatures)
    signature_data = serialize_signatures(signatures)
    print("signature_data:", signature_data)
    print("Signatures size:", len(signature_data))
    compressed_signatures = compress(signature_data)
    print("Compressed signatures:", len(compressed_signatures))

    print("Total sizes -> ticket: %s, signatures: %s" % (len(serialized_data), len(compressed_signatures)))
    print("Total compressed sizes -> ticket: %s, signatures: %s" % (len(compressed_ticket), len(compressed_signatures)))

    ### STEP 2 ###
    pass
