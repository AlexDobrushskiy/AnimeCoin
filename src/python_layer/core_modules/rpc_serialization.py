import nacl
import time
import msgpack

from core_modules.blackbox_modules.signatures import pastel_id_write_signature_on_data_func,\
    pastel_id_verify_signature_with_public_key_func
from core_modules.blackbox_modules.helpers import sleep_rand, get_sha3_512_func
from core_modules.helpers_type import ensure_type, ensure_type_of_field

MAX_SUPPORTED_VERSION = 1
NONCE_LENGTH = 32
MSG_SIZELIMIT = 4*1024*1024

VALID_CONTAINER_KEYS_v1 = {"version", "sender_id", "receiver_id", "data", "nonce", "timestamp", "signature"}


def ensure_types_for_v1(container):
    sender_id = ensure_type_of_field(container, "sender_id", str)
    receiver_id = ensure_type_of_field(container, "receiver_id", str)
    data = ensure_type_of_field(container, "data", list)
    nonce = ensure_type_of_field(container, "nonce", bytes)
    timestamp = ensure_type_of_field(container, "timestamp", float)
    signature = ensure_type_of_field(container, "signature", str)
    return sender_id, receiver_id, data, nonce, timestamp, signature


def verify_and_unpack(raw_message_contents, expected_receiver_id):
    # validate raw_message_contents
    ensure_type(raw_message_contents, bytes)
    if len(raw_message_contents) > MSG_SIZELIMIT:
        raise ValueError("raw_message_contents is too large: > %s" % MSG_SIZELIMIT)

    # raw=False makes this unpack to utf-8 strings
    container = msgpack.unpackb(raw_message_contents, raw=False)
    ensure_type(container, dict)

    if container.get("version") is None:
        raise ValueError("version field must be supported in all containers!")

    version = ensure_type_of_field(container, "version", int)

    if version > MAX_SUPPORTED_VERSION:
        raise NotImplementedError("version %s not implemented, is larger than %s" % (version, MAX_SUPPORTED_VERSION))

    if version == 1:
        # validate all keys for this version
        a, b = set(container.keys()), VALID_CONTAINER_KEYS_v1
        if len(a-b) + len(b-a) > 0:
            raise KeyError("Keys don't match %s != %s" % (a, b))

        # typecheck all the fields
        sender_id, receiver_id, data, nonce, timestamp, signature = ensure_types_for_v1(container)

        if receiver_id != expected_receiver_id:
            raise ValueError("receiver_id is not us (%s != %s)" % (receiver_id, expected_receiver_id))

        # TODO: validate timestamp - is this enough?
        assert (timestamp > time.time() - 60)
        assert (timestamp < time.time() + 60)

        # validate signature:
        #  since signature can't be put into the dict we have to recreate it without the signature field
        #  this validates that the message was indeed signed by the sender_id public key
        tmp = container.copy()
        tmp["signature"] = ""
        sleep_rand()
        raw_hash = get_sha3_512_func(msgpack.packb(tmp, use_bin_type=True))
        verified = pastel_id_verify_signature_with_public_key_func(raw_hash, signature, sender_id)
        sleep_rand()

        if not verified:
            raise ValueError("Verification failed!")
        # end

        return sender_id, data
    else:
        raise NotImplementedError("version %s not implemented" % version)


def pack_and_sign(privkey, pubkey, receiver_id, message_body, version=MAX_SUPPORTED_VERSION):
    if version > MAX_SUPPORTED_VERSION:
        raise NotImplementedError("Version %s not supported, latest is :%s" % (version, MAX_SUPPORTED_VERSION))

    sleep_rand()

    if version == 1:
        # pack container
        container = {
            "version": version,
            "sender_id": pubkey,
            "receiver_id": receiver_id,
            "data": message_body,
            "nonce": nacl.utils.random(NONCE_LENGTH),
            "timestamp": time.time(),
            "signature": "",
        }

        # make sure types are valid
        ensure_types_for_v1(container)

        # serialize container, calculate hash and sign with private key
        # signature is None as this point as we can't know the signature without calculating it
        container_serialized = msgpack.packb(container, use_bin_type=True)
        signature = pastel_id_write_signature_on_data_func(get_sha3_512_func(container_serialized), privkey, pubkey)

        # TODO: serializing twice is not the best solution if we want to work with large messages

        # fill signature field in and serialize again
        container["signature"] = signature
        final = msgpack.packb(container, use_bin_type=True)

        sleep_rand()
        return final
    else:
        raise NotImplementedError("Version %s is not implemented!" % version)
