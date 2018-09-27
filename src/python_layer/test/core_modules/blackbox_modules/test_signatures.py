import unittest
from unittest.mock import patch

from core_modules.blackbox_modules.crypto import get_Ed521
from core_modules.blackbox_modules import keys
from core_modules.blackbox_modules.signatures import pastel_id_write_signature_on_data_func, \
    pastel_id_verify_signature_with_public_key_func


class TestSignatures(unittest.TestCase):
    def setUp(self):
        self.input_data = b'THIS IS SOME TEST INPUT TEXT'
        self.Ed521 = get_Ed521()
        self.private_key = b'TEST RANDOM BYTES'
        self.public_key = b'\x03#m\xfa\xf4\xb9\xcf\xc8\x8cO\x9e\xca\xb8O\x17o\x07Ak\x0e:\x1fW\xdfi"\xb6' \
                          b'\x06\xc1\x1a\x8dR\xa5\x07G\xc3\x1a\xbbF\xc6L\xe6jo{D\x0f\x8c\x89O\xb1\xfb\x9f' \
                          b'\x970$\x98\x8d\xf0\xeb\x91\xbc\x06\x14X\x00'

    def test_generated_key(self):
        with patch('nacl.utils.random', return_value=b'oofioCh7da2Eet6gi9owohB2do9ohsup'):
            privkey, pubkey = keys.id_keypair_generation_func()

        signature = pastel_id_write_signature_on_data_func(self.input_data, privkey, pubkey)
        verified = pastel_id_verify_signature_with_public_key_func(self.input_data, signature, pubkey)
        self.assertTrue(verified)

    def test_signatures(self):
        signature = pastel_id_write_signature_on_data_func(self.input_data, self.private_key, self.public_key)
        verified = pastel_id_verify_signature_with_public_key_func(self.input_data, signature, self.public_key)
        self.assertTrue(verified)

    def test_bad_types(self):
        with self.assertRaises(TypeError):
            pastel_id_write_signature_on_data_func(b'', b'', None)
        with self.assertRaises(TypeError):
            pastel_id_verify_signature_with_public_key_func(None, b'', b'')
