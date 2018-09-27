import nacl
import base64

from nacl import utils

from .crypto import get_Ed521

Ed521 = get_Ed521()


def id_keypair_generation_func():
    input_length = 521*2
    private_key, public_key = Ed521.keygen(nacl.utils.random(input_length))
    private_key_b16_encoded = base64.b16encode(private_key).decode('utf-8')
    public_key_b16_encoded = base64.b16encode(public_key).decode('utf-8')
    return private_key_b16_encoded, public_key_b16_encoded
