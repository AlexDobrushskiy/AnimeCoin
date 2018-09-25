import base64
import random
import time

from .crypto import get_Ed521

Ed521 = get_Ed521()


def pastel_id_write_signature_on_data_func(input_data_or_string, id_private_key_b16_encoded,
                                           id_public_key_b16_encoded):
    if isinstance(input_data_or_string, str):
        input_data_or_string = input_data_or_string.encode('utf-8')
    private_key = base64.b16decode(id_private_key_b16_encoded)
    public_key = base64.b16decode(id_public_key_b16_encoded)
    time.sleep(0.1 * random.random())  # To combat side-channel attacks
    signature = Ed521.sign(private_key, public_key, input_data_or_string)
    signature_b16_encoded = base64.b16encode(signature).decode('utf-8')
    time.sleep(0.1 * random.random())
    return signature_b16_encoded


def pastel_id_verify_signature_with_public_key_func(input_data_or_string, id_signature_b16_encoded,
                                                    id_public_key_b16_encoded):
    if isinstance(input_data_or_string, str):
        input_data_or_string = input_data_or_string.encode('utf-8')
    signature = base64.b16decode(id_signature_b16_encoded)
    public_key = base64.b16decode(id_public_key_b16_encoded)
    time.sleep(0.1 * random.random())
    verified = Ed521.verify(public_key, input_data_or_string, signature)
    time.sleep(0.1 * random.random())
    return verified
