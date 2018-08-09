import nacl
import sys
import base64
import random
import time

from animecoin_modules.animecoin_signatures import animecoin_id_write_signature_on_data_func, \
    animecoin_id_verify_signature_with_public_key_func

from animecoin_modules.helpers import sleep_rand, get_sha3_512_func
from animecoin_modules.animecoin_compression import compress_data_with_zstd_func, decompress_data_with_zstd_func


MESSAGE_FORMAT_VERSION = '1.00'
MIN_NONCE_LENGTH = 500
MAX_NONCE_LENGTH = 1200
MAX_MESSAGE_SIZE = 1000
NONCE_LENGTH = random.randint(MIN_NONCE_LENGTH, MAX_NONCE_LENGTH)


def verify_raw_message_file(raw_message_contents):
    if isinstance(raw_message_contents, str):
        if len(raw_message_contents) < 4000:
            signature_string = '\n\ndigital_signature: \n'
            start_string = 'START_OF_MESSAGE'
            end_string = 'END_OF_MESSAGE'
            id_character_set = 'ABCDEF1234567890'
            nonce_character_set = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
            version_character_set = '1234567890.'
            assert (raw_message_contents[0] == '\n')
            assert (raw_message_contents.split(start_string)[0] == '\n______________________\n\n')
            assert (len(raw_message_contents.split('\n')) == 42)
            assert (len(raw_message_contents.split(signature_string)) == 2)
            message_contents = raw_message_contents.split(signature_string)[0]
            assert (message_contents.split(end_string)[-1] == '\n\n______________________\n')
            assert (message_contents.replace('\n', '')[-22:] == '______________________')
            hash_of_combined_message_string = get_sha3_512_func(message_contents)
            signature_line = raw_message_contents.split(signature_string)[-1].replace('\n', '')
            assert (isinstance(signature_line, str))
            assert (len(signature_line) == 264)
            assert ([(x in id_character_set) for x in signature_line])
            message_contents_fields = message_contents.split('______________________')
            assert (len(message_contents_fields) == 11)
            for current_field in message_contents_fields[1:-1]:
                sender_string = '\n\nsender_id:\n'
                assert (len(message_contents.split(sender_string)) == 2)
                if current_field[:len(sender_string)] == sender_string:
                    senders_animecoin_id = current_field.replace(sender_string, '').replace('\n', '')
                    assert (len(senders_animecoin_id) == 132)
                    assert ([(x in id_character_set) for x in senders_animecoin_id])
                receiver_string = '\n\nreceiver_id:\n'
                assert (len(message_contents.split(receiver_string)) == 2)
                if current_field[:len(receiver_string)] == receiver_string:
                    receivers_animecoin_id = current_field.replace(receiver_string, '').replace('\n', '')
                    assert (len(receivers_animecoin_id) == 132)
                    assert ([(x in id_character_set) for x in receivers_animecoin_id])
                    assert (senders_animecoin_id != receivers_animecoin_id)
                timestamp_string = '\n\ntimestamp:\n'
                assert (len(message_contents.split(timestamp_string)) == 2)
                if current_field[:len(timestamp_string)] == timestamp_string:
                    timestamp_of_message = float(current_field.replace(timestamp_string, '').replace('\n', ''))
                    assert (timestamp_of_message > time.time() - 60)
                    assert (timestamp_of_message < time.time() + 60)
                message_format_version_string = '\n\nmessage_format_version:\n'
                assert (len(message_contents.split(message_format_version_string)) == 2)
                if current_field[:len(message_format_version_string)] == message_format_version_string:
                    message_format_version = current_field.replace(message_format_version_string, '').replace('\n',
                                                                                                              '')
                    assert (len(message_format_version) < 6)
                    assert ([(x in version_character_set) for x in message_format_version])
                    assert ('.' in message_format_version)
                message_size_string = '\n\nmessage_size:\n'
                assert (len(message_contents.split(message_size_string)) == 2)
                if current_field[:len(message_size_string)] == message_size_string:
                    message_size = int(current_field.replace(message_size_string, '').replace('\n', ''))
                    assert (message_size >= 10)
                    assert (message_size <= 1000)
                message_body_string = '\n\nmessage_body:\n'
                assert (len(message_contents.split(message_body_string)) == 2)
                if current_field[:len(message_body_string)] == message_body_string:
                    message_body = current_field.replace(message_body_string, '').replace('\n', '')
                    assert (len(message_body) == message_size)
                    assert (message_body == message_body.encode('utf-8', 'strict').decode('utf-8', 'strict'))
                random_nonce_string = '\n\nrandom_nonce:\n'
                assert (len(message_contents.split(random_nonce_string)) == 2)
                if current_field[:len(random_nonce_string)] == random_nonce_string:
                    random_nonce = current_field.replace(random_nonce_string, '').replace('\n', '')
                    assert (len(random_nonce) >= 500)
                    assert (len(random_nonce) <= 2500)
                    assert ([(x in nonce_character_set) for x in random_nonce])
                sleep_rand()
            verified = animecoin_id_verify_signature_with_public_key_func(hash_of_combined_message_string,
                                                                          signature_line, senders_animecoin_id)
            sleep_rand()
            return verified, senders_animecoin_id, receivers_animecoin_id, timestamp_of_message, message_size, message_body, random_nonce, message_contents, signature_line


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
            message_size = message_size
            message_body = message_body
        else:
            raise ValueError("Error, message body is too large!")
    else:
        raise TypeError("Message body is not str!")

    linebreak = '\n______________________\n'
    combined_message = linebreak + '\nSTART_OF_MESSAGE:\n'
    combined_message += linebreak + '\nsender_id:\n' + pubkey + linebreak
    combined_message += '\nreceiver_id:\n' + target_pubkey + linebreak
    combined_message += '\ntimestamp:\n' + str(timestamp) + linebreak
    combined_message += '\nmessage_format_version:\n' + message_format_version + linebreak
    combined_message += '\nmessage_size:\n' + str(message_size) + linebreak
    combined_message += '\nmessage_body:\n' + message_body + linebreak
    combined_message += '\nrandom_nonce:\n' + random_nonce + linebreak
    combined_message += '\nEND_OF_MESSAGE\n' + linebreak
    hash_of_combined_message_string = get_sha3_512_func(combined_message)

    # sign and append signature to the combined message
    signature_on_raw_message = animecoin_id_write_signature_on_data_func(hash_of_combined_message_string, privkey, pubkey)
    signed_combined_message = combined_message + '\n\ndigital_signature: \n' + signature_on_raw_message

    # compress and generate signature
    compressed_signed_combined_message = compress_data_with_zstd_func(signed_combined_message)
    hash_of_compressed_signed_combined_message = get_sha3_512_func(compressed_signed_combined_message)
    signature_on_compressed_message = animecoin_id_write_signature_on_data_func(hash_of_compressed_signed_combined_message, privkey, pubkey)

    sleep_rand()

    return signed_combined_message, compressed_signed_combined_message, signature_on_compressed_message
