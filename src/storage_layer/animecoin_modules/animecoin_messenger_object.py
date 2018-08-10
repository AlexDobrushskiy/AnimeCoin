import nacl
import sys
import base64
import random
import time
import json

from animecoin_modules.animecoin_signatures import animecoin_id_write_signature_on_data_func, \
    animecoin_id_verify_signature_with_public_key_func

from animecoin_modules.helpers import sleep_rand, get_sha3_512_func
from animecoin_modules.animecoin_compression import compress_data_with_zstd_func, decompress_data_with_zstd_func


MESSAGE_FORMAT_VERSION = "1"
MIN_NONCE_LENGTH = 500
MAX_NONCE_LENGTH = 1200
MAX_MESSAGE_SIZE = 1000
NONCE_LENGTH = random.randint(MIN_NONCE_LENGTH, MAX_NONCE_LENGTH)


def verify_raw_message_file(raw_message_contents):
    if isinstance(raw_message_contents, str):
        if len(raw_message_contents) < 4000:
            hash_of_combined_message_string = get_sha3_512_func(raw_message_contents)

            msg = json.loads(raw_message_contents)
            VALID_KEYS = {"sender_id", "receiver_id", "timestamp", "message_format_version",
                          "message_body", "random_nonce", "digital_signature"}

            a, b = set(msg.keys()), VALID_KEYS
            if len(a-b) + len(b-a) > 0:
                raise KeyError("Keys don't match")

            id_character_set = 'ABCDEF1234567890'
            nonce_character_set = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'

            senders_animecoin_id = msg["sender_id"]
            assert (len(senders_animecoin_id) == 132)
            assert ([(x in id_character_set) for x in senders_animecoin_id])

            receivers_animecoin_id = msg["receiver_id"]
            assert (len(receivers_animecoin_id) == 132)
            assert ([(x in id_character_set) for x in receivers_animecoin_id])
            assert (senders_animecoin_id != receivers_animecoin_id)

            timestamp_of_message = float(msg["timestamp"])
            assert (timestamp_of_message > time.time() - 60)
            assert (timestamp_of_message < time.time() + 60)

            message_format_version = int(msg["message_format_version"])

            message_body = msg["message_body"]

            random_nonce = msg["random_nonce"]
            assert (len(random_nonce) >= 500)
            assert (len(random_nonce) <= 2500)
            assert ([(x in nonce_character_set) for x in random_nonce])

            sleep_rand()
            signature_line = msg["digital_signature"]
            verified = animecoin_id_verify_signature_with_public_key_func(hash_of_combined_message_string,
                                                                          signature_line, senders_animecoin_id)
            sleep_rand()

            return verified, senders_animecoin_id, receivers_animecoin_id, timestamp_of_message, len(message_body), message_body, random_nonce, signature_line


def verify_compressed_message_file(senders_animecoin_id, compressed_binary_data,
                                   signature_on_compressed_file):
    if isinstance(compressed_binary_data, bytes):
        if sys.getsizeof(compressed_binary_data) < 2800:
            hash_of_compressed_message = get_sha3_512_func(compressed_binary_data)
            if len(senders_animecoin_id) == 132:
                sleep_rand()
                verified = animecoin_id_verify_signature_with_public_key_func(hash_of_compressed_message,
                                                                              signature_on_compressed_file,
                                                                              senders_animecoin_id)
                sleep_rand()
                if verified:
                    try:
                        decompressed_message_data = decompress_data_with_zstd_func(compressed_binary_data)
                        return decompressed_message_data.decode('utf-8')
                    except Exception as e:
                        print('Error: ' + str(e))


def read_unverified_compressed_message_file(compressed_binary_data):
    if isinstance(compressed_binary_data, bytes):
        if sys.getsizeof(compressed_binary_data) < 2800:
            try:
                decompressed_message_data = decompress_data_with_zstd_func(compressed_binary_data)
                return decompressed_message_data.decode('utf-8')
            except Exception as e:
                print('Error: ' + str(e))


def generate_message_func(privkey, pubkey, target_pubkey, message_body):
    sleep_rand()

    # generate random nonce
    random_nonce = str(
        base64.b64encode(nacl.utils.random(NONCE_LENGTH)).decode('utf-8') +
                        str(time.time()).replace('.', '')).replace('/', '').replace('+', '').replace('=', '')

    # set timestamp
    timestamp = time.time()

    # set message format
    message_format_version = MESSAGE_FORMAT_VERSION

    # validate message body
    if isinstance(message_body, str):
        print('Nonce Length:' + str(len(random_nonce)))
        message_size = len(message_body)
        if (message_size - NONCE_LENGTH) < MAX_MESSAGE_SIZE:
            message_body = message_body
        else:
            raise ValueError("Error, message body is too large!")
    else:
        raise TypeError("Message body is not str!")

    msg = {
        "sender_id":               pubkey,
        "receiver_id":             target_pubkey,
        "timestamp":               str(timestamp),
        "message_format_version":  message_format_version,
        "message_body":            message_body,
        "random_nonce":            random_nonce,
        "digital_signature":       None,
    }

    # TODO: use HMAC for signing!

    msg_serialized = json.dumps(msg)
    hash_of_combined_message_string = get_sha3_512_func(msg_serialized)

    # sign and append signature to the combined message
    signature_on_raw_message = animecoin_id_write_signature_on_data_func(hash_of_combined_message_string, privkey, pubkey)
    msg["digital_signature"] = signature_on_raw_message
    msg_serialized_with_signature = json.dumps(msg)

    # compress and generate signature
    compressed_signed_combined_message = compress_data_with_zstd_func(msg_serialized_with_signature)
    hash_of_compressed_signed_combined_message = get_sha3_512_func(compressed_signed_combined_message)
    signature_on_compressed_message = animecoin_id_write_signature_on_data_func(hash_of_compressed_signed_combined_message, privkey, pubkey)

    sleep_rand()

    return msg_serialized_with_signature, compressed_signed_combined_message, signature_on_compressed_message
