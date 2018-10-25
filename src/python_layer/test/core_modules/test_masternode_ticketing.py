import asyncio

import unittest
from unittest import mock

from core_modules.zmq_rpc import RPCException, RPCServer, RPCClient
from core_modules.settings import NetWorkSettings
from core_modules.masternode_ticketing import IDRegistrationClient, ArtRegistrationClient, ArtRegistrationServer

from test.mock_objects import MockChainWrapper


class TestIDRegistration(unittest.TestCase):
    def setUp(self):
        self.privkey = b'TEST RANDOM BYTES'
        self.pubkey = b'\x03#m\xfa\xf4\xb9\xcf\xc8\x8cO\x9e\xca\xb8O\x17o\x07Ak\x0e:\x1fW\xdfi"\xb6' \
                      b'\x06\xc1\x1a\x8dR\xa5\x07G\xc3\x1a\xbbF\xc6L\xe6jo{D\x0f\x8c\x89O\xb1\xfb\x9f' \
                      b'\x970$\x98\x8d\xf0\xeb\x91\xbc\x06\x14X\x00'
        self.chainwrapper = mock.MagicMock()
        self.chainwrapper.store_ticket = mock.MagicMock(return_value=None)

    def test_registration(self):
        address = "eABqvpZCDAYAq11g65kKqUt3DuKKxebRfV5"
        c = IDRegistrationClient(self.privkey, self.pubkey, self.chainwrapper)
        c.register_id(address)


class TestArtRegistrationWithMockMNs(unittest.TestCase):
    def setUp(self):
        # 1x1px png with color FF4D00 and opacity 0.8
        self.image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x01\x03\x00\x00\x00' \
                          b'%\xdbV\xca\x00\x00\x00\x03PLTE\xffM\x00\\58\x7f\x00\x00\x00\x01tRNS\xcc\xd24V\xfd\x00\x00' \
                          b'\x00\nIDATx\x9ccb\x00\x00\x00\x06\x00\x0367|\xa8\x00\x00\x00\x00IEND\xaeB`\x82'

        self.privkey = b'm\xf4\x99\xbc\x13\xce\xc4\xa8x?\xd2\xd3\x99E?\xf4\x91\xdc\xa39\xbf\x03Y\xceB@)\x02\xf7\xf6\xe4bx\xba[\x04\xa4\x80\xc4c%\xbe\xba$\xf5\x19\xf6x\x82F\x84\xe9\xd0f@\xe7(\x01\x07\x94\xf5-\x82\xd9\x02\x9aX[\xa1`\xd8\x19\x03\x9d\xcb\xadK\xb3\xf5+\xaa;\x9f\xf5\x00\xf4]\xf6w\xf6V\xef\xdcj\xe5}\x159\n\xc4\xd2\xf2\xf6\xe9\x9dY\t\xcbH\\\xb3\xc6\xb5L\x05\xc6\xb5\x9eG5\xcc\x9f\x04PcL\x98\x85\xa2\xe0\xa6\xce\x8d\x19J=i\x15\x10\xff:h\xc3\xa9i#:\x99\x7f\xee\x19\x8c\xfa6\x8fU\xbb\xc9RYUR6\xb1\x1b\x93*j\xcc\xe9\x9a\x96\x13\xa0\xda\xa99\xa2\x87\x88>\xb8\xfc\x1e\xab\xd7\xd1\x0c\x9fd\xeaO\xd3\x05_\xacL\x85\xec\xc9\xc7\xc0}n\xc7S\xd1\xf1\xdc\x97\xee\x01\xfc\xbarw\xf4\x0e\xf8\x14\xf07\xb6y[\x99=+\xed\x8b\x11\xa8\xd6^"\x07)\xe9\xa3r\xddx \x809\x8b\xa3\xfb\xbd\x01\xfb\xf7\xf9D]V\xdb;\xcb_\x1co\xd1\xdf\x02\x03\x19u\x98\xaf\x91\x03\xc0\xd8\xef\xd3/\x07\x8fD\xd3\x1b\xad\xc5\xa0p\x9a\x08.\xed*\xc9\xa7\x9a.\xab\x19^\xef\x9c\xe14d\xf0\x02[\x9a\xec-\xe3\xa2\xd8p\xca\xe8\x9bA\x13\x84\x8a+h\xa5D\xfb\x05\xed\xf5I\xcb\xab\xe6\x08W\x85S\xde|\x9eY\xbdK\xa7\xff\x9b\x8a]\t\xb2\xea\x828\xe9S;\x8e\xac\xe9\xa3\xb8\xe1\xd3\xbcU\x84\x88{P\xaa\xc7\x91\x1f\xd0$\xd3[\xe0(\xa4+\xe2\xd1\xdd\xac!\xc6\xc9\x9e\x8b\xe6\xf1\x069J\xd2\x97\xf0\'b\xb4\xe4\xe1\xc4\xd1,V\xcdv\xc4\xb6\x18\xbc}\xea\xfbH\xb3\x85\xa6\x04\x9a\xbb\xd6\x0e\xfc\xf5%g\xa4\xaf4\xbf\xd1\xc0}\xc6e\xfd\xd8\x12fT\xcf\xb8\xf9a\xb1\xf7\xfe3\xc3:\xfbJ\xb9\x08,\x7fm\xca\x8d\xafQ\xdb\x9far\x8dhR\x04\x08\xb7\xc3\x85_\xe8\xe2\xf2\xb29\xbf\x15\xf08E\x1d\xb2\xc6\xb0F\x8e\xf6;p\xb7\x07\xcb\x0cU-w\xa2\xe1\xd2\xfdV\x1c\xc0\x1aRW\xfd\x97\x98\xfe\x1c\x15\xb2#\x86 \x84\xfb\xf2\x8c\xf5n\xb3\x87\xae\x85\xab\xb5\\bb$\xbc\xcf\xf1\xd4\x97\xa9\x13\x87d5\x99\x0c-\xf9\xaeh\xc3\xd5\xc8\x14\xca\xfc\x12\xde5\x1d[H\xd7\x01[\x9c9\x98p2\xb1\xdb,\x99\x05\xd8\xc4\xfc\xdb\r\xfbb\x9e\xaaz\xb4$\x83\xa4\x16\xf5L\xf3\xde\x0b8\x8c\xec\x9c\xcc\xa0\xb7;Ez\tx\xdc\xb3\xbe\x12J\x01\xdc\x19\xac%\x8d\xccA\xe4\xbd\xba\x94N\x90\xe3^\xb4HVA\xc7\x87A\xe0\xd6t\xb8\x06\x8e\xedW\xeeh\x87\x158Q\xce\x9c\x81\x9ae\xb6\xca]\xbb0\xbd\xdc\xa0\x13\xebfd\xceL\x02\xc6\x82j!\xf4\xa9^\xb9\xb1\x14&\xc0\xda\xcf\xa3\x94\\\xb37\xecl\xf62W\x05\x8av\xe6\x1c\xc5\xd2\x13\x8e\x9en\xe7j\x88\xed!j]U\xa97\xbd\xea\xdb\x89e\xd7/\xf9\x88\xcbh*\xaa\xe9(\xcdC\t\xf0\xb6\x11\xb9:\xc1\x88X\x9c\xbd\xbeKY{\xce\x88\x95#$n_V~DT\x9f\xe2\x03@\x8e\xec\xdd\xf9\x123\x08\x80\x124\xbd\xc6\xacY\x8a\xf0:q>g\xf3\x82\xe5\x10\xf5\xf9Z\xad\x04U\xc7s\xdf3\xb8\x8c#\xec\x85\xbfO\xa1\xfb9\x9f\xd5\x98G\xc8(\x1eX\xb4\xdf\xe3\xa8Tr>z\\\xb5\xaf\xe5\x96\x1e\x1e\x8a\xe6\x1c\xf8\xee\x15v\x11\x15l\xa2\xd7\x0f\xc8/\x7f\xfe\xbb\xea\xfa\xde\x17\xb2\xf0\x85\xf4\xe2\xd30[(\x1b\xc9{*\x04\xb4\x87yQ\xfelS{s\x05Wh\xd1-\x05\xe6\x1cx\xf0y\xc0Q\xde\xdb\xc4U\xdaP<\x17\x19\xefU\x97\x92{8y\x01C\xe9Ey\xa9\xf8J\x9f\xc4\xd3\x11l\xe9N\xc9\x82\x892<\xe5\xb4|\xb8\x1c\x86\x8eY\'\x10\x97G\x87\xdfF\x92\xa5Avjg\xbb\'\xb7\x15R\x92Pl\x12\x10\x1ff\xac(T\xe7j\x84\x14R- n\xd4o\x8e\xf4\x9b\x13\x8b-\x8c\x8eg\x1fxX\x03t{lf\x0bS2\xccx\x1c\xfdE\xea\x7f$\x0b\x9c\x04\xf4\xacVeFKU\xe1Gx\xc7\x1d\x8f\x05\xcb$\xc1\x11\xd9\x9d\xa2v\xcey!c\x9e.\xd4\xcf5H\xbf\x81JBa\x9dW'
        self.pubkey = b'\xb7<\x9f\xb9\xad\xacqr+\n\xee\xa6\x02\xe6h(\xd3\xd3~z\xa32\x92\xbc8M\x00$O\x9e\xd5\xfbk\xa4k\xea\x85\xdf\x0b\xb6\xa1\x88?\x9b\xe0\x81\xfe\x14\xcd\xb02\xef\xb3\xee\xff\xb0\xc50\x94z\xca\x9d<\xed\x9a\x01'

        # set up mocks
        import logging
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(' %(asctime)s - ' + __name__ + ' - %(levelname)s - %(message)s')
        consolehandler = logging.StreamHandler()
        consolehandler.setFormatter(formatter)
        logger.addHandler(consolehandler)

        self.nodemanager = mock.MagicMock()
        self.chainwrapper = MockChainWrapper()

        self.chunkmanager = mock.MagicMock()

        # set up mock MNs
        mn0_privkey = b'\xf1DV\xbe\xdb7i\xe3\xf2\x17Pb\xe3\x11\x81\xdb|\xe6\xed\xff\x84\xbe/\xcdyzJ\xbf\n-\xd1\xb3\xf6\xe3h\xc4\xd9\xc1fY\x17\x14\xca\xefU\xfdO\xe1\xfa\xbbZ]R\xad\xcd\'QX\xc1\xca\xdd3\n:p\xb8\xea\xc0\xb6\x11\xaa\x155o\xd8!\x85\xd3\xefQ\x0bo\x1a\x8b\\\xdb\xa3M$\xe1af\xac\xbaj\xad0\xaeoj\x995\x06yly\x1d\xe0\xdb\xefE\xd3W\x1fO\xa3\x929,\xde\x1f\xbe\x82VZ\x8b\xbdm%\x92\x87>_\xec\xd2\xc7!%\xed\xcer7\xdbd?y\x0f\xcd\x95q\xf0=\xfa\x8d)&\xc0\xf8\xa9\xc0\xa5\xd7\x96\x87!\xe0\xb8\xc1\x0e\xbf\xc1\xf0\x83y\x8cW4\xe0\xd1\rU\xb6\xe4\xb5\xe5\\!\x19e!\xe2\x83z\xe1\xf3\x94\x81{\xec\x93\xce,\x89=\xa0Z]\'k\x10+@V\xc0\xc4G\xa8\x065\xc0\x9d\x89\x83\x9d\xc1\xc4\xcc:\xb2\x97t$\x9a\xd9\x14\xbb\x86\xd6\xd4s\xccy!\xa9^\x82\xd5"\xf3\x9c\xa203\xae;X\x0c\xe35A\xf3}\x1a\x1f.\x02T\xb0)\xb0\x85\xbe\xaf\xc6#\x84\xf5\xcae)\x97R[\x93\xbdrl\x80w6M\xc9\x15F\xecE\x8d\xb0\xba.\x15\xf3`\xe5\x98}\'\xb5\x89\xeacc\x0c\xa6\xf8\xd8\xff\x193\xa9\x93x\x0e\x02\'\x8a\xf9\xd1Y\xd4\x84\r\x81\x9b~aR\xb40L\x98\xfb\x1e\xe1)p\x1e@\xf6\x91\xc2\xab>\xc2\x8f\xa1i\x9d\xea\xd0$\x05=f\x9e\xdc\x1b|o2\xd9\x99C+9:TXE\xe4\x02\xa9\xec\x83rb"\xc2\xde6\xeb+\xd9\xe1\xae\xa2hq\xa6C\xb0\xd1\xa3\x93\xa3i\xc2\'\xb8\xfb\xef\xd3\xf1_\x13\x8d\x8dB\x8e\xd4\x92FD9\x8e\x14\xe6\xa6\x185i\xef\xc2\x98H\x06\x12\x95\xca\x93\xb4\xdaq\x0c\xd4Hc*\xd6\x81\xfb\x91$9\xc8^\x00\xff\x9e\xab\x19\x1c\xcaqi\'\x81\xe8\xd8\x97j\xfbt\xfe%\xae\xbd)N\xe0\xf5\xe6Ro9\xfd76ZW\xb8\x85\x8b-^o\x1a1\xbb\xfa\x83\xe8KR\xd6\xb2Y\xc7\x81\xb9\xa6\xc3I\xe1\xc5a\xe0J\xeb$\xc1r\x9a2\n""l\xbb\xe9\'\x99\x0c\xc3\xd9\xfaf\xd8o\x00\xe3\xfe\x1aWm*Y\x91\xcft\x03\xa5\x1b\xc0P\xf1A\xe0\xa5;U\x8a\x84\x9e\xda:\xf2\xbd\xf8l\xa9g\x9f\xa5\x98\xb0\xea\x82u,\xc1\xd5\x86[Z\x99\xca(\xb2\xfaR\x13\xbc\x84\x10\x861s\xbb\x92\xa5\x97\xfaH\xe8%\xa0\xeb\x889\x81\xff\x01,\xcb\x0f\xa5\xdf\x12\xbdB\xa5s\x8bL\xc9\xad\x1e\xf4\xbe\xef\x9c\xb3\x06\xbf\xeb\x7f\xdc\xe9\xdc\x85\x7fc\xbcRo#T\xbb,\xd3\x16\xfe&}\xb1\xa4\x89\xe1\xed\xc7\x0c\x94\xb0!\x81\xaca~lm\x9a6\xab\x19\x80\xbd\xad\xafh\xbc"\xad\x03|\x93\x812S\x13\x8fU\xd4\xb28\x13\x18\xf1\x13\xbe\xaa\xdc&_\xc3M\x7f@3\xa8e\x89\xff1 +D\x87fj*\x8eB\xce\x84\xefG:\x01\xde\xd8+U\xf0\x9b\xaa$j\xbd\x0e\xe03\x9f\x11\xe39\x16\xa7\xdd\xf3G\xddv\xcb\xc4\xa9\xab\xe1\x0e\xbe8\xf3\x87\x0f\x7f\x11\xc9\x97\xa4\xc3P\xba\xd9eD\xc6\xa7]T\x91\xab\xc0&OLM\xe4 \t\x8f4K5\xa9\xadP\x84\xcdw^Q=\x8b>\x9a\xae\x13\xff\x11\x19\xc2\xc0\x99V\'\x1bW/\xe7$\xe0\x0c\xbe\x1c\x86\x95j\xf9Z\xc2\xcc\x8c5\x04\x7f#\xa4|\x02\xd3\x95\xdeU\x05Yu<\xcbT\x07\'\xb9b\xea\xdah$\x89\xad\xc8\xf9\xa0\xba\x81Iv\xe5\xfd\xf4\xae\xdb\x16\xc8\xd6\xa9bVL;\xf4\xf7\xcb\x00\xde\xe4\xe4#\x05\x8d\x94\xe9y\x8d\xe9\xab\xec\x14\x8f\xacI\x9b1\xc6&\xf8c\xa5\xcd-e\x95\xcc\xc5\xd5\xf3k\x96+O\xb4\xa7\xf9.\x1b*\x92\xbe\xa2\xff\\\x9e\x10r\x89\xd2w\xd6a\xd1\x8eH\xe4\xb1Q\n\xc8k\xf1$m\xbc\x02\xa5\x11\xd7\x14\x10\x1c=\xf4\x1bj\xb0\xf9\xafR>\\WMW\x8c\xdf\xb2\xbd\xfe\xb3\xd5\xd9\r\rz: \x1c\x0c$CsN\xef\xb1\xd7c\x0f\x01\x1f\x11M.\xcd~\r7\x919\x1c\x94\xc7\x83vw\x08\xc8a[\xaa\x0e\xf5\x92\x9eg\x02\x85\xe8\x93u\'\xc4\xa2\xef\xe6I\x05\xe5\x99]\x0b3R\xfc\xe1'
        mn0_pubkey = b'v\xe0\xd8\xbd#E\x11,)\x96\x9a\x0c$KA\xa5\x88 \x87\xd7\xb4H\x1b\tP\xcc7[\xb4\xd9N\x94j\xca7v\x99`\x89\xf90\x86\xfcc\xfc\xd5\x92/w\x1e\x1c\x8a\x9f\x05\xc6\x17a)\x9c\xc3pP\xf2)\x04\x01'
        mn0_artregistrationserver = ArtRegistrationServer(mn0_privkey, mn0_pubkey, self.chainwrapper, self.chunkmanager)
        mn0_rpcserver = RPCServer(0, "127.0.0.1", "10001", mn0_privkey, mn0_pubkey)
        mn0_rpcclient = RPCClient(0, self.privkey, self.pubkey, 1337, "127.0.0.1", "10001", mn0_pubkey)
        mn0_artregistrationserver.register_rpcs(mn0_rpcserver)

        mn1_privkey = b'`}\xf2\x9b\xb7\xf0\x17\x15\x92j\x9c\xc3\x06\xf4RM\x1fRk\x82\xb0\x0c\xc1\xddkZ\xde\xa9\x99h*v\xc4Z\xce\xdfuh\xe7I\n\x008--\x0e\x0b\xc9\x07\xd1(\xfb\xa2\r\xa9N7\x8a!\xce#\xbd9U\xde\x16\xaeoe\x13\x15\xec\x1a\xcc\x1e\xda-\xa7u\xed\x082\xe7\xce\xb7\xe2\xb4\x9f\x9a\xcc\x8a\x0e\x16\xd7\xe0Ay\xcd\t\x1f]\xbe\xe9c\xe2\xcbl\x8d[\xea\x99\x03\x00\x8f\x83]\xe5\x1ch\xedN(\x02\xcdT\xd6\xa3\x1cb\xc08\x8b\xd6\xab\x1e\xf0N\xc1Yj\x1c%r\xdd\x85\x96\x9f\x9c\xc0p{\t\xe1o\xa3\x1am\xa8\xe8\xeb|y(q\x10\xdf\x85JZ\xff\xbf*\xdfr\xf2A\x1e\x8a\x12-\x8a\xfb\xa5\x85\xb0\x99\x0f\x88\x1e\xf2\xd9\x84\xc2\x1d\x830\x08\xa9\xc7\xba\x16\xf9\x1dX\xf87\x02\xa2$\x80cA\x1e\x1e\xf4s\x9bt\xdcx/\xc1\x07\x15i\xc7\x80\xe3\x0f+\xf9?N\xe1/@\xbe\xcf\xae\x02Xm\x18-m\xdf\xfb\xaa\x83\xbah\xf3y\x941\xe8$T\x82\x0e\x98\x91\xeaU\xd9R\xca\xde4\xcb*\x0b\ry\x8b?r\x88\xf7\x1d3\x83^\x90\\\xbcU$gUb@\xdc\x02\x127N13\x03\x87\x06:\x06\x1ddU\x0e\xb24\x07\x8d&\x07\xf8\xcf\xf3\xcf\x04\x8f\xe55Dj\xcf\xd9\xc5\x92\x04\xe9\xc9\xa1\xddC\xd6\x0e\x93\x1b\x8b\xa8r\x82g\xa1\x97\xa0F\xe30\x86\x89\xed.\x0b\xac@\xe7\x07;\xb0\xc6\xa8\xdd}\x08u\'\xdf\x81\xfd\xf0\xda`\x83L\xf0\x9f{\x8a\x16\x07Sk?\x87t\xe1\xc8\xdb\x8d=\xd8-\xbaA\xb5\\\xbe\x98I\xae\x9c\xd5\xe2\x9aD+&\x90\x93\xfe\xe3@&\x989\x86\xe0\xeb4\x8b\x0b\xa6\xc0pZf\x15]\xe82\x00\xe3)\xdb+\xd9\x99\x9e\x85\xa8\xf3G\x16\x0e\x89\xaaJ\x82*#\x05\xf7\xdfB\x01\x18O\r\x99u\x18\xe2\x7f\x1f\xd2t?\xa9^\xf9\xcc\x8b\xa3Sw\xae:w\x9a\xc5\x1a&\x80\r\x9d\xde6\x0bu\xd2PQz!\x82\x87\xe9\xf6H%\xdf\x8c*x\xab\xc0\x1b:\xcam\x1e\xc0\r\xf7\x8fY\xf8+\xd0:\xba\xc92\xa9E7\xae\x9a\x8dE&\xbea?\xd3#\x8a\xfc\xc6ca@y7\xc2\xe7\x91c\xbb[\xc2v\x04e\x02\xe1#\x189o+\xf0\x00GO<\xb1n\xea\xa6G\xcb\xda\xb4\xa5\xfa\x16\x95O+\xaa\xdc\x91\x83\x0bh\x817\x07\t\xa7HG\x9b=\xd3IZ\xa8\xc1\x92\x8a6\x04\xf4\xb9\xf9\xc4\x89\x14fQ\xf8\x0f\x1fD\x8c\xdb\x8f\t\xf0\xd43\x99|cD\t\x04\x02.)`\xceW\xc8\x9f;\x07T\x11\xea\x8e\x92\x12\x14=>]\xfd\x08[\x07\xa2\x8b\xb7\xb41\xd9\x0e\xe0>\x00`@o\xfa\x8d[\xe66\xb2\x97\xaem\xf3b7\xc7[\xa1\xa9\xbc\xb2)\x92\x92\xcf\x1d\x98\xaf\xbe\xaf\xc8\x89\x85\xb0+@\xe1\xf3\x14\x12\xa8\x03\x93{\xcb\xe6\x9d\xb9g.\x0bK:\xf1ft\x7f\xa4Lf\xa1&\xe0:U\xfd\x19\xdaZ2\x00\xc5O\x99\\\x00\x1a\x9fVd\xfa\xbcj\x87\xe2\xc1s\xec\xe0"\x80\xf6k\x0c+\x87\xf6R\xbc\x8b\xb6\xce\x9fd_\xa8\x8a\xbcV\x9b\x90\xa1s-\xc0\xf3\xc5\x98\xc9\xcc\xfb\x9f\xd7\xc1vr|YH\x98G\x03n\x81\x02\xce>w\x97\xb0\xbd\x14\xca\x9a\xeb\x0e\x92\x97\xf1sc\x9c\xf3<\n>\xe5\xb4A1!\xa9\xa6_\x11\xc0z{\xe3\x80\xf5\x9f`\x80\xcb\x93\x9c\xa4Mn".M\x05 \x03\x98r\x8a\xd2\xcaGw3)\x0bq\xdb\x92\x10V\x12\x05\xad\x8a\x14\x1f\xd1\x1d\x04q\xd8\x84\xa5`*\x8d:n\x96]\xf8\xca\xbd\x13\xb2\x1e2\x84\xfd\xf3\x95\x03\x16y\xfc\xba\x03\x81\xa2_\x07\xefk\xd8\xa8vT=\xef!\xe96\x81\xbf\xc4\x8bd6\x12\x05?>O\x0f&\x03G\x82ht\x04^a\xe9u\x15\xb9\x98MX\x1c\x91\xbf#\x10=\x0e\xe1*\xdc\xbe\x94\xe2{\xa3[/\xd2s\xeah\xc0h\xaf%Y8\xf0\xc7\x04\xb1\n\x8f\x0cK|nt\xdd\x07m!\'c\x84v\xb0\x18[gHE\x08\nX\xc1\x95\xdc\x97`#u@\xf5\xf8\xa0\x05z&\x1am\xab\x91\x83\x1fp\xd5>\xfa\xf9:\xb4\x00cB\xea\x83\x01\xf8mj\xfc\x081\xfe\'\x01'
        mn1_pubkey = b'a`\x0cCUK<\n\x96\xfe\xab\xa9S\xaa\xd7\xcamtc~o\xfcv\xa77\t\xd1\xee\xfb\xde)\xeaS\xd8\xf6\xad&\x05\x14\xbb]/\xcaf\xaa\x1b\x9cy?c\xb4Zx)\x13\xe4\xdc\xc1\xdc3b\x95\xf2.s\x80'
        mn1_artregistrationserver = ArtRegistrationServer(mn1_privkey, mn1_pubkey, self.chainwrapper, self.chunkmanager)
        mn1_rpcserver = RPCServer(1, "127.0.0.1", "10002", mn1_privkey, mn1_pubkey)
        mn1_rpcclient = RPCClient(1, self.privkey, self.pubkey, 1338, "127.0.0.1", "10002", mn1_pubkey)
        mn1_artregistrationserver.register_rpcs(mn1_rpcserver)

        mn2_privkey = b'\xe2\x84\xffb\xe9>\xccw\xe0g1\x8c\x05aW\x82d\xbb\x9aXT\x08\xd1\x01\xc6@\xce7\xd9\xa9a\x08\xa3\x04\xa1rY{r\xeb~d]\x94\xa1\x9b\x88p}\x1c\x94\xb2\xadY\xfdI(f\xb6\'\xbe>\xba\xdb\xe1e\x82\xa5Q\xeb\xb5w\x98\xb0\\\xd5a\xb9*\xf86\x9aE~BL\xf8\xbe\xffk,F\x1a}\xc4E\xea\xf3\x10@\xf7\xf3I\xc2\xea\xba#\x0c\x17\xdd\xac4J\x1b\xe7\xa0#\x96\xc4\xcc\xe8[\x18\x9b\xa6\xae\x1c\xb5t\xb7\x00\xb0=\xe3{S\xec\xf3\x11X\t\x9b\xd3i\xf2\xd6W\x85\xae\xf9l$J\xd4g\x8f/x\xde\xe8\x12\x01\x80\xf6\xb5=\xbf\xaf\x7f\x01\x98\xbe\x90l4v\xe1\xf7\xfc\xf6rV\x07f|\\K|8\xa4\xae\xf1a`<q\xe7x\xbf\xa5\x81\x9f\xdcu\xb2\xff\xb1\xd2r\xb4\xab`J\x02\x8c\xbc\x18\x01~\x8e\x15\xa0\t\x00\x8d\xc3Y\n\xc9i\xa8\x8c\xe7\x9f\x07R\x9e\x1f\x8e\xc7&u~2\xc0m\xc8\x05\x12H\x91\xabe\xd6\x96{\x85\xd8\x88\xa8E\xe0|\x17\xe8\x14\xec\xdc\xf9&\x0bc_Y"6\xc4\x06\xbd]L\x10\x00p\xefN@\xaf\x0c\x195\xf1\xcf\xea\xf9*\x84\x80\x0fu\xe3\xd7\x1dj|.\xe9\xaav\xa2\x9f\xd2\x80P\xb5\xc4\xb9l\xbe\x1a\xfa6R\xdc\xdcH\x1a#\x9aYc\xa6\xcaWp\x06\x15\xec\xeb6\xd9\x8e|\x10\x1b\x05\xca\x85\r\xfa\xd3uC#\xa5\x07v\x8d\xc7\xcbU<\xd5.\x80\xee\xe8\x1a]b\xbe\x89\xb7\xfd\x94\xf8f,\xa3{\x14E\xad\xb2\xba\xe0\xbe\xd3o!\x1bK\xdeT\xf4f\r\xe4*\x9d\n\x96\x10\xf2\x1a\xfd(\xa9\xf9\xa1\x07\xd2/\x86\xd4\xfc{\xca\xd66\xbc\x8d\xa4\x96\xa2\x01\xc4\x9f8\x92\x0f\xb7>\x11\xd0\xf7m:\xa0-\xff\\\xa3g\x9e\x8a\xcc\xfa~\xc5}:\xe5\xeb\xc1\xaa\x16\x1e\xab\x05\xc9n\xafc5!x\xce\xc3&\xe7q\x95\x8c\xd4>"\xd1\x89\xfa\xf0\x0e<fI&lC\xd3\xa6I\xe1\xcc\x81\xe2\xc4\xbbja\xe1\x87ss\xa3N=\xc8\x82$g\x13U\x99{\xd6{\xa8\xb8\x8e\xe7\xc8\x19\xdd\x16P:{\xd5\x02\xfa\x17\x0e\xfai\'\\a\\\xe0\xa8&r\xb5\x83\xcc\x85Cc\x08\xfeI[uK%\xb9\xc5\xd6\xb16\xa5q,!\xec{O\xb7\xab\xc1 U\xf4\x8f\x1f\x86vl\x0b\xc1h\x14S\x93\xeeB\xa1Vv\xca\xf0<$\x8a\xa2\x12\xb78\xee\x9d\x90W=\x08\x19\xc0\x8f&\xb4"\x0c\xa8\xb2\x9d28\x1f\\\x97\x04\x111Y\xccg\xcf\xbc\r\xe39\xab\xafY\xf7L^|\x01\xae\xd0\xc6~\xf2\x11\xe8\x9e\x90\x17S\x10N\x14\xa4%\xf2\xb7\xcd\t\xe04QV\xb7\x1b\xc0/\xec\x1f\xe3\x1b\xaetP\xf0^\x1eKfaX\xe5\xdcG\x83\x88\x1c\x8aB\xebr\xc0`\xc1\xa2\xdb)\x12\xfa\xe64^\xf1\\-\xed\x9e \xe2\x16\xa76\xce\x83\xbf\xa4\x011J\x86uC5\x11\xbe\x100\x99\xb3_\xcaGT\x90\x16x[^V\xef\xbe+\xffg\x12\xa1\xd7N\xd8\xa2\xcd\x8e@\xa6r^n\x88\xcfO\x19\xd8\x82\xb5w(\x9d\xc9\x19\x080-gX\x1c\x9d\xd9\x0b\xdeaR4\x94\xdb\x84\xef\x17$\x8d\xc8,.]\x12\x02!%\x98\xdc\xdf"\x17G\xc5\t\xbd\xc3T8\x89\x03[;x\r\xed\xb6\x8b\xe0\xeb\xae>\xfb\xec=o\xd9~\xe7U]\x88g\xc3\x19\xb3\xdf\xf2\x02\xd7,\x9e\xa7\x9awE \'/2\xc6=\xbc\x1c\xb6\x85}\xa8\x96d@\x16\xf0\x87\xb5\x80H\xefn\x98c\x1e\x1b,\xc1\xc4\xd5p\x00\'\x10\xcb\xe7[V\x8b\xb1\x921\xa7\xc4\xf0\xccX1\x82O\xd7o9n\xda\x05${i>\xc6<\xb0]\xb7\x0e\xd2\xaaOK_\':9a_\x8e\xa5\x82\x08\xf0\xce\xc8Cy\x94\x86\x92y\xa4\x1b\x8d\x93t.j\xbax\x94\xf6\x1de\x90\xde\x880l\xec\r\xef}l\x98\xd8c\x0e\x03#\xfe \x1b\x92\xfa\xb0\x80\x85\xfa\x85.\x0b\xfc>\xda\r.\x9a\x97\x88\x89R\xa8\x99~?\xc7%\xf8\xbd\xed\xf3\xb9\x94\xe7"\x7f#\x93\xeb:\xb0\x80\xe5\xf6z\x81\xb1Y\xad\xfa\xdc\x81\xed\xb0\x1d\xd9]IH,\x15\xae\xee\xdd\x02LY\xb5\xc4m\xae\xe8\xcaZ:\x83&'
        mn2_pubkey = b'Lg9X\x9fn#T\x9b\xf2\x93\x83\xee^\xc0\xc7cq+\xaey\x08\x91\xab\xa4\x88z\r\xd6c<\x0cEn7o \x9e\xf5\xab\x84\x1d\x9em\x86\xeey\xeaUa\x81"\x8d\x03\xda\x926\x0c\x04\xf8\xa7dC\xfa\xf2\x00'
        mn2_artregistrationserver = ArtRegistrationServer(mn2_privkey, mn2_pubkey, self.chainwrapper, self.chunkmanager)
        mn2_rpcserver = RPCServer(2, "127.0.0.1", "10003", mn2_privkey, mn2_pubkey)
        mn2_rpcclient = RPCClient(2, self.privkey, self.pubkey, 1339, "127.0.0.1", "10003", mn2_pubkey)
        mn2_artregistrationserver.register_rpcs(mn2_rpcserver)

        self.masternode_rpc_servers = [mn0_rpcserver, mn1_rpcserver, mn2_rpcserver]
        self.nodemanager.get_masternode_ordering = mock.MagicMock(return_value=[mn0_rpcclient, mn1_rpcclient, mn2_rpcclient])
        self.chainwrapper.get_masternode_order = mock.MagicMock(return_value=[mn0_pubkey, mn1_pubkey, mn2_pubkey])

        # set up mock dupe detector
        mock_dupe_detector = mock.MagicMock()
        dummy_fingerprint = [0.0 for x in range(NetWorkSettings.DUPE_DETECTION_FINGERPRINT_SIZE)]
        mock_dupe_detector.compute_deep_learning_features = mock.MagicMock(return_value=dummy_fingerprint)
        self.dupedetector = mock.MagicMock(return_value=mock_dupe_detector)

    @mock.patch('core_modules.settings.NetWorkSettings.VALIDATE_MN_SIGNATURES', new=True)
    def test_registration(self):
        artreg = ArtRegistrationClient(self.privkey, self.pubkey, self.chainwrapper, self.nodemanager)

        with mock.patch('core_modules.ticket_models.DupeDetector', new=self.dupedetector):
            loop = asyncio.get_event_loop()
            tasks = []
            image_registration_task = artreg.register_image(
                image_data=self.image_data,
                artist_name="Example Artist",
                artist_website="exampleartist.com",
                artist_written_statement="This is only a test",
                artwork_title="My Example Art",
                artwork_series_name="Examples and Tests collection",
                artwork_creation_video_youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                artwork_keyword_set="example, testing, sample",
                total_copies=10
            )

            # assemble task list
            tasks.append(image_registration_task)
            for mn in self.masternode_rpc_servers:
                tasks.append(mn.zmq_run_forever())

            # run until first task (the only one that can finish) finishes
            done, pending = loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED))
            actticket_txid = done.pop().result()

            for task in pending:
                task.cancel()

            # stop event loop
            # loop.stop()

            # find final activation ticket and validate signatures
            final_actticket = self.chainwrapper.retrieve_ticket(actticket_txid)

            # validate signatures by MNs
            final_actticket.validate(self.chainwrapper)