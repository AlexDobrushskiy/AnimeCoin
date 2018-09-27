import unittest
from unittest.mock import patch

from core_modules.blackbox_modules import keys


class TestKeys(unittest.TestCase):
    @patch('nacl.utils.random', return_value=b'TEST RANDOM BYTES')
    def test_key_generation(self, mock_method):
        privkey, pubkey = keys.id_keypair_generation_func()
        mock_method.assert_called_once_with(521*2)
        self.assertEqual(privkey, b'TEST RANDOM BYTES')
        self.assertEqual(pubkey, b'\x03#m\xfa\xf4\xb9\xcf\xc8\x8cO\x9e\xca\xb8O\x17o\x07Ak\x0e:\x1fW\xdfi"\xb6'
                                 b'\x06\xc1\x1a\x8dR\xa5\x07G\xc3\x1a\xbbF\xc6L\xe6jo{D\x0f\x8c\x89O\xb1\xfb\x9f'
                                 b'\x970$\x98\x8d\xf0\xeb\x91\xbc\x06\x14X\x00')
