import unittest

from core_modules.blackbox_modules.crypto import get_Ed521


class TestCrypto(unittest.TestCase):
    def setUp(self):
        self.data = b'TEST DATA'
        self.privkey = b'544553542052414E444'
        self.pubkey = b'F4D204259544553204153465341464153534146E35A89624674F564E43961CB0AAF3924C' \
                      b'0F9458A8D29C75AB152BCB6C3486A83A0E5780FAAAE51126CFEA4152856E82452E18C0D95C2' \
                      b'BD20305BB93E8BD2B36A3C80'
        self.signature = b'\xd2_\xff\x82\xdb\xc87\r\xbf\xaa\xbe\x85\x08\xfcT\x98<\x06*ki=\xa7WW(\xb1' \
                         b'\x13\x93jI\xce\xb1X\ns\x9b\x8e\x9c\x83Jp7\\sI\x83\xb0q\xc5\xaf\x960o\xa2\x1f' \
                         b'\xf0\x16\x80^\x93\xef\xb0\x0b\xe5\x00\x9a\xdd\xff\xbd`\xce\xe8\xc1\xfe\xbfkP' \
                         b'\x95"\xaf\xca\xdbM|\xd9\xab\xf4\x89D\xad\rF\xf0\xeb\x92\xe3[Puv-,p\xbcJ\x13\xad0' \
                         b'\xdd\x19\xba$Z`^\x04A\x05\xb7\xfe\x00^0\xba\tQ\x02\x8f<\x7f\x00'
        self.ed521 = get_Ed521()

    def test_crypto_signing(self):
        signature = self.ed521.sign(self.privkey, self.pubkey, self.data)
        self.assertEqual(signature, self.signature)
