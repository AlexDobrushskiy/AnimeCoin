import nacl
import time
import msgpack


from .animecoin_signatures import animecoin_id_write_signature_on_data_func,\
    animecoin_id_verify_signature_with_public_key_func
from .helpers import sleep_rand, get_sha3_512_func


MAX_SUPPORTED_VERSION = 1
NONCE_LENGTH = 32
MSG_SIZELIMIT = 4000

VALID_CONTAINER_KEYS_v1 = {"version", "sender_id", "receiver_id", "data", "nonce", "timestamp", "signature"}


def verify_and_unpack(raw_message_contents):
    if not isinstance(raw_message_contents, bytes):
        raise TypeError("raw_message_contents has to be bytes!")

    if len(raw_message_contents) > MSG_SIZELIMIT:
        raise ValueError("raw_message_contents is too large: > %s" % MSG_SIZELIMIT)

    # raw=False makes this unpack to utf-8 strings
    container = msgpack.unpackb(raw_message_contents, raw=False)
    if not isinstance(container, dict):
        raise TypeError("container has to be dict!")

    if container.get("version") is None:
        raise ValueError("version field must be supported in all containers!")

    version = container["version"]
    if not isinstance(version, int):
        raise TypeError("Version must be an int!")

    if version > MAX_SUPPORTED_VERSION:
        raise NotImplementedError("version %s not implemented, is larger than %s" % (version, MAX_SUPPORTED_VERSION))

    if version == 1:
        # TODO validate all types!

        # validate keys for this version
        a, b = set(container.keys()), VALID_CONTAINER_KEYS_v1
        if len(a-b) + len(b-a) > 0:
            raise KeyError("Keys don't match %s != %s" % (a, b))


        # TODO: validate all the fields!

        sender_id = container["sender_id"]
        receiver_id = container["receiver_id"]
        timestamp = float(container["timestamp"])

        assert (timestamp > time.time() - 60)
        assert (timestamp < time.time() + 60)

        data = container["data"]
        nonce = container["nonce"]

        # validate signature:
        #  since signature can't be put into the dict we have to recreate it without the signature field
        signature = container["signature"]
        tmp = container.copy()
        tmp["signature"] = None
        raw_hash = get_sha3_512_func(msgpack.packb(tmp, use_bin_type=True))

        sleep_rand()
        verified = animecoin_id_verify_signature_with_public_key_func(raw_hash,
                                                                      signature, sender_id)
        sleep_rand()

        return verified, sender_id, receiver_id, timestamp, len(data), data, nonce, signature
    else:
        raise NotImplementedError("version %s not implemented" % version)


def pack_and_sign(privkey, pubkey, receiver_id, message_body, version=MAX_SUPPORTED_VERSION):
    # TODO: validate parameters

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
            "timestamp": str(time.time()),
            "signature": None,
        }

        # serialize container, calculate hash and sign with private key
        # signature is None as this point as we can't know the signature without calculating it
        container_serialized = msgpack.packb(container, use_bin_type=True)
        signature = animecoin_id_write_signature_on_data_func(get_sha3_512_func(container_serialized), privkey, pubkey)

        # TODO: serializing twice is not the best solution if we want to work with large messages

        # fill signature field in and serialize again
        container["signature"] = signature
        final = msgpack.packb(container, use_bin_type=True)

        sleep_rand()
        return final
    else:
        raise NotImplementedError("Version %s is not implemented!" % version)
