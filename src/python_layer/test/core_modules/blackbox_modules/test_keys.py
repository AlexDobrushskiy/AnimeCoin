import unittest
from unittest.mock import patch

from core_modules.blackbox_modules import keys


class TestKeys(unittest.TestCase):
    @patch('nacl.utils.random', return_value=b'TEST RANDOM BYTES')
    def test_key_generation(self, mock_method):
        privkey, pubkey = keys.id_keypair_generation_func()
        mock_method.assert_called_once_with(521*2)
        self.assertEqual(privkey, "544553542052414E444F4D204259544553")
        self.assertEqual(pubkey, "03236DFAF4B9CFC88C4F9ECAB84F176F07416B0E3A1F57DF6922B606C11A8D52A50747C31ABB4"
                                 "6C64CE66A6F7B440F8C894FB1FB9F973024988DF0EB91BC06145800")
