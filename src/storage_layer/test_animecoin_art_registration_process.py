import sys
import base64
import zstd
import keras
import pickle

# TODO: do we want to use sha3_512 for this?
from dht_prototype.masternode_modules.animecoin_modules.animecoin_dupe_detection import DupeDetector,\
    combine_fingerprint_vectors
from dht_prototype.masternode_modules.animecoin_modules.helpers import get_sha3_512_func_bytes
from dht_prototype.masternode_modules.animecoin_modules.animecoin_signatures import animecoin_id_write_signature_on_data_func, animecoin_id_verify_signature_with_public_key_func
from dht_prototype.masternode_modules.animecoin_modules.animecoin_keys import animecoin_id_keypair_generation_func
from dht_prototype.masternode_modules.models import ArtRegistrationRequest, load_ticket,\
    serialize_ticket, serialize_signatures, load_signatures, ArtActivationTicket
from dht_prototype.masternode_modules.model_validators import ARTREGISTRATION_KEYS
from dht_prototype.masternode_modules.animecoin_modules.animecoin_compression import compress, decompress


# TODO: This was set by Jeff, do NOT change yet!
TARGET_SIZE = (224, 224)


# step 1
# X artist constructs reg ticket
# X sign ticket
# X for every MN:
#   o validate registration ticket
#     X MN validates signature
#     X MN validates hash
#   o blockchain validations
#     o is a unique registration (does not exist yet on the chain)
#   X MN validates ticket
#   X if all is well, MN signs
# o make sure validator works right
#   o validate metadata
#     o validate thumbnail
# X blockchain verifies ticket with all signatures

# step 2
# X artist constructs verification ticket
# X sign ticket
# o for every MN:
#   o validate activation ticket
#     o signatures are correct
#     o hash is correct
#   o blockchain validations
#     o validate that activation ticket belongs to registration ticket
#   o reg ticket validations
#     o regticket contains the same list of MNs
#     o regticket has not been activated yet
#     o regticket contains a file hash which is not registered yet
#     o regticket contains the hash of the actual file hash
#     o regticket contains the actual metadata hash
#     o validate metadata
#       o thumbnail
#     o check fingerprint for dupes
#     o check image for nsfw
#   o sign


def create_registration_ticket(image_file_path, pubkey, dupedetector, combined_list):
    # 1) Artist fills registration ticket

    image_file_data = open(image_file_path, "rb").read()

    # read the actual image file
    # TODO: get the fingerprint from the actual file
    # image = keras.preprocessing.image.load_img(image_file_path, target_size=TARGET_SIZE)
    # fingerprints = dupedetector.compute_deep_learning_features(image)
    # combined = combine_fingerprint_vectors(fingerprints)
    # combined_list = combined.values.tolist()[0]
    print("FINGERPRINTS", len(combined_list))

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
        "IMAGE_HASH": get_sha3_512_func_bytes(image_file_data),
        # "IMAGE_FINGERPRINT_HASH": get_sha3_512_func_bytes(combined_list),
        # "IMAGE_FINGERPRINTS": combined_list,
    }
    ticket = ArtRegistrationRequest(datadict)

    # serialize and sign ticket
    serialized_data = serialize_ticket(ticket)
    serialized_hash = get_sha3_512_func_bytes(serialized_data)
    return serialized_data, serialized_hash


def client_sign_ticket(serialized_hash, privkey, pubkey):
    return animecoin_id_write_signature_on_data_func(serialized_hash, privkey, pubkey)


def create_verification_ticket(reg_ticket_id, pubkey):
    datadict = {
        "ART_REGISTRATION_TICKET_ID": reg_ticket_id,
        "ARTIST_PUBKEY": base64.b64decode(pubkey),
    }
    ticket = ArtActivationTicket(datadict)

    # serialize and sign ticket
    serialized_data = serialize_ticket(ticket)
    serialized_hash = get_sha3_512_func_bytes(serialized_data)
    return serialized_data, serialized_hash


# TODO: perhaps move this to into the proper validator?
def __validate_data(serialized_data, serialized_hash):
    # validate hash
    if serialized_hash != get_sha3_512_func_bytes(serialized_data):
        raise ValueError("Hash does not match!")

    # unpack and validate data
    ticket = ArtRegistrationRequest(load_ticket(serialized_data))

    # validate signature on data
    pubkey = base64.b64encode(ticket.ARTIST_PUBKEY)
    if not animecoin_id_verify_signature_with_public_key_func(serialized_hash, client_signature, pubkey):
        raise ValueError("Validation failed!")


def masternode_sign_registration_ticket(data, data_hash, mn_privkey, mn_pubkey):
    __validate_data(data, data_hash)

    # all is well, sign the ticket
    return animecoin_id_write_signature_on_data_func(data_hash, mn_privkey, mn_pubkey)


def blockchain_verify_ticket(data, data_hash, signatures):
    __validate_data(data, data_hash)

    for pubkey, signature in signatures:
        if not animecoin_id_verify_signature_with_public_key_func(data_hash, signature, pubkey):
            raise ValueError("Validation failed for signature: %s" % signature)


if __name__ == "__main__":
    # TODO: remove this, this is only to speed up development
    fingerprint_db = pickle.load(open("/home/synapse/tmp/animecoin/fingerprint_db_all_nns.pickle", "rb"))
    filename, entry = fingerprint_db["2ef9cd445d39f3aa550c11bef5284253ef99cc93615cdde47fd045b48bb11a42"]
    combined = combine_fingerprint_vectors(entry)
    combined_list = combined.values.tolist()[0]

    image_file_path = sys.argv[1]
    privkey, pubkey = animecoin_id_keypair_generation_func()
    masternodes = []
    for i in range(3):
        masternodes.append((animecoin_id_keypair_generation_func()))

    # dupedetector = DupeDetector()
    dupedetector = None

    ### STEP 1 ###
    # create ticket
    registration_data, registration_hash = create_registration_ticket(image_file_path, pubkey, dupedetector, combined_list=combined_list)
    # print("Serialized data:", serialized_data)
    print("Ticket created, len:", len(registration_data))

    # compress ticket
    samples = list([x.encode("utf-8") for x in ARTREGISTRATION_KEYS.keys()])
    compressiondict = zstd.train_dictionary(8096, samples)
    compressed_ticket = compress(registration_data, compressiondict=compressiondict)
    print("Compressed:", len(compressed_ticket))

    # sign ticket
    client_signature = client_sign_ticket(registration_hash, privkey, pubkey)

    # have MNs validate and sign ticket
    signatures = [(pubkey, client_signature)]
    for mn_privkey, mn_pubkey in masternodes:
        mn_signature = masternode_sign_registration_ticket(registration_data, registration_hash, mn_privkey, mn_pubkey)
        signatures.append((mn_pubkey, mn_signature))

    # submit to blockchain -> verify all signatures
    blockchain_verify_ticket(registration_data, registration_hash, signatures)
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

    print("Total sizes -> ticket: %s, signatures: %s" % (len(registration_data), len(compressed_signatures)))
    print("Total compressed sizes -> ticket: %s, signatures: %s" % (len(compressed_ticket), len(compressed_signatures)))

    ### STEP 2 ###
    # construct verification ticket
    registration_txid = 123456789   # TODO: fill this out properly
    activation_data, activation_hash = create_verification_ticket(registration_txid, pubkey)

    # sign ticket
    client_signature = client_sign_ticket(activation_hash, privkey, pubkey)
