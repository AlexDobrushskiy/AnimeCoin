import base64
import random
import time

from .animecoin_crypto import get_Ed521
from .helpers import AnimeTimer

Ed521 = get_Ed521()


def animecoin_id_write_signature_on_data_func(input_data_or_string, animecoin_id_private_key_b16_encoded,
                                              animecoin_id_public_key_b16_encoded):
    print('Generating Eddsa 521 signature now...')
    with AnimeTimer():
        if isinstance(input_data_or_string, str):
            input_data_or_string = input_data_or_string.encode('utf-8')
        animecoin_id_private_key = base64.b16decode(animecoin_id_private_key_b16_encoded)
        animecoin_id_public_key = base64.b16decode(animecoin_id_public_key_b16_encoded)
        time.sleep(0.1 * random.random())  # To combat side-channel attacks
        animecoin_id_signature = Ed521.sign(animecoin_id_private_key, animecoin_id_public_key, input_data_or_string)
        animecoin_id_signature_b16_encoded = base64.b16encode(animecoin_id_signature).decode('utf-8')
        time.sleep(0.1 * random.random())
        return animecoin_id_signature_b16_encoded


def animecoin_id_verify_signature_with_public_key_func(input_data_or_string, animecoin_id_signature_b16_encoded,
                                                       animecoin_id_public_key_b16_encoded):
    print('Verifying Eddsa 521 signature now...')
    with AnimeTimer():
        if isinstance(input_data_or_string, str):
            input_data_or_string = input_data_or_string.encode('utf-8')
        animecoin_id_signature = base64.b16decode(animecoin_id_signature_b16_encoded)
        animecoin_id_public_key = base64.b16decode(animecoin_id_public_key_b16_encoded)
        time.sleep(0.1 * random.random())
        verified = Ed521.verify(animecoin_id_public_key, input_data_or_string, animecoin_id_signature)
        time.sleep(0.1 * random.random())
        if verified:
            print('Signature is valid!')
        else:
            print('Warning! Signature was NOT valid!')
        return verified