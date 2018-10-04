import asyncio

import unittest
from unittest import mock

from core_modules.zmq_rpc import RPCClient, RPCServer, RPCException


class TestZMQRPC(unittest.TestCase):
    def setUp(self):
        self.logger = mock.MagicMock()

        self.s_chunkmanager = mock.MagicMock()

        self.s_nodeid = 0
        self.s_ip = "127.0.0.1"
        self.s_port = "11111"
        self.s_priv = b'L\xb6\xc3\xc7\x9f\x90\xb3\xb0\xb5\x9e\xb8z\xa9\x8c\xe0\xfct\xfd\xc5\xf9\x1cx\xe2\xdd\x0c\x84k\xf6\xb6\xb1\xd1N\xfaK\x1a\xd5\xcf\xb3\xb5\xdc\xb8d\xf7\xbbLQ\xfcQ\xf6\xb2W\xc6\xab\x87\xa0\x83l\xc4\x96\xa5\x02A\xb4\xddZ\xa5%\x1b\xeb\xab\xe0\xc2\xbb\xba\xb18w\xc3\xe8G\xf7\xf9\xea\xbf\xb3\x93\xbe\x9c\x16:\xd2\xc3\x9d\xeb\xc5\x0c\xab\'>\xcex\x82ye\xaeX5\x1a\xad\xe6!\x16\xe5\x9b:\xc9 \x7f>P(\x1c\x9f\xefpif\x0e)r%\xf6,\xae?\x8c\xad\xa7b\xfc\xfc\x85\x19\xb8\xb3\x06\xed!\xc1P\x1a(ej*.\x9b\xd2\xa0\xcf\xfalH!\xc8\x865\xae\xab\xd7\xb6\xae\xe5\xc6\x14\xdb\t\x9anQo2\xe6\xd4z2^\x18\x05\x0e\xf8\n\xe9%\xfe,\xa13\xf4\x88\x84~\xb5G\x05\x99\x86Z\x81\xdar\xb9\x9e\x0e\xe0{\xd1,Oen\x1e(\xe3\xf2\x11\xe1\na\x8c%\xae\x86&aLc\x08Z\xc3\'\xb3\x17\xe0\xb7\xd0\xd6\xb4\x89\xf6q\xbcg 18\xed\x0e\xfd\xb0\'\x03V\x89\xab\x0f\xe5.\xffg\x90\xe2\xf0\t\xf0\xfel\xe7\xf5\x07b\xf3\xedh\xd0-=k^4@-q\x03Z\x19\xf5Ve\xaeM4~\xf5E<8nm:\xd3V\xeb\xa9YX\x1e\xfd\x86\xd2\x83v\xab\xf97<\xbc\x93\x02\xd3\x1a\xad>+\xd2\x1c\x1f\x99B\xd9\x17\xbeI\xbf\x06" \xc0\xe3\x0ee\\\r\x98Y\xa9\xba\xce\xcbH\xcbZ\xee\x81Z\xfb\xb7\t\x0ci\xdf%zt\xb2\xa4M\x07\xdc\xbdZ\xee\x88\xff\xf3\x110\x92O;\x16\x02\x01\xee O\xfd5\xff\xd1\x848_\x9fOR,+\x19?\xc5S"\x9e\xbe7*\xe2\xc1\x1c\xf5\x8b61\x94\xc2&\xa7\xa2\x85\xa9\x8e_0\x8e\x8c\xb8\xf7\x93\x8f\xeeGt\xb2\x13\xa2\xacT\xdb\x91o\xf7\x8f\xfa\xad\x06+\xea\x86\xa5_\xed\xbe\xde\x05\xd6\x0c\x9f%\xf0\xe7\xbd\xc4^\xa1y\xcfU!\xf5\x15o\x19\x13\x1et\xe8\xf1K\x9bG\x96&\x17H3\xac\xa6\xc5\xc0\xf8\xc8\x1a\x85\xc8\xc3\x8d\xe5\x7f\xa5\xf4\x1a\x9eoRs\x06\xd3C\x94\x01G\x94\xe6\x83\x83\x03\xa8\xdb\x84\x05\x14\xf7\xb0c\x96\x0e\x91\xfa\xdc\xd7npI\x00G7\x98 \x8f\x91\xe4VJ\xe8\xe5\xdd|\xb0[!\'W\xa4a\x1e%\xe1\x93\x06g\xb9\xd6\xb1\xdb\xc2\x8f\x82\xb3J\x16S\x89\xc5\x05\\\x93\xa4\xc7H\xb0o7\xab=\xc5@\xb1\xd5S_\x06\xde\x89\x9a!B!B\xd5\xd7\xd1\xbf\x90+\xec\'!\xdcJ\x83Z\xb8\x0f\xd7\xa4<\xd8\x90\xd1\x17REy\x86"S\xe2\xfc\x0c\x15n\\\x863\x0b\x8c1\'\x8d\x82\xe7l \x1a\x9a\x9a\x99\xd0\xb3\xe0\xd9T\x05\x88\x14L\xed\xac\xc8\xcc\xebJ\xd7\xd3\xc7\x7fdd\x0c\x11"\xa9\xf2R\xbe\x9cBVA\xc9\xe2u\xae\xb6\xc7$o\xa0\' \x8e\xab\x804\x106{\x80\x04\x83\xaaO\x1e\x88*x\xbc\x1cu=\xcb\x85*5M3\xadq\x85{z\xe1#\xce\xae\xf6Y\xe0?=0$\x9c_\x90\xee7(!\x1b\x16\x11\xf3j\xb5\xa6\x1c\x9e\xdc5\xdb3\xbe\x8e\x0e;\xe4\x8f\xb5\x15\x18:\xf7y\xc2\xc51Ke\x1c\xc2t\x1ed\xe9\xb4j\x9e\x85\x08O\xc4b>\xf5\x89\xca\x0b$%\x94\xcfI\xe8\x9c\x85\x7f\xf3\xa6iP]\xb8\x06\xd8\xb9\x9f\x01\x11\xaa\xf4\xf8\x15\xe6P\x0fI\xe7V\x0c;N\\\xbc\xa6`\xc2N\xac\xd3\xa9r\x9725,\x97\xf0\xf7C\xd2\x1f[Br\xc9\xa9\xc9\xbeFe\x99\x16\xbch\xc1\x9d\xbfJa\x811\xce^\xbe\xe1G\x83:\x07\xda\xc0Em\xa09\xe04`\x84Ba0V\xe3\x04w\xb9\\\xad\xe4\x15WD\x1f\xe4\x9a\xc1z\t%Tv\xe8\x0c\xa0l\xaaW\xc3\xe6\nQL\xc3fG\xf3\x89\x02kn\xbb\xcbm\x16\xc8\x95`\xf8l\x95\x0fj\xfe\xd7q(s\xb0\x96W\x99h\x17^U\x93\xcf2i\xd51\x8b\xd4\xc4\x1c\xfb\x0f\xf4_\xd3\xf7a\x17\xf4\xab\x82v:\xa0\x03\x1c\x8c`~\xf3\xc0\xca\xcb\x99+\xf3R/\xe4\x11\x92\x9aW+U\x16VQ\xb9 \x90\xbef\xc1\xd2\xd8\\\xcf~_\x101R>V\xf5\xf9\x99\xa7\xf1B\xdd\n\xf3\x03\xe9\x0e\x83!\xde\x00\xee\xc0\xf4'
        self.s_pub = b'\x0c\xd7\x1bx?\x12\xf4\x8bM\xe4\x07\x124\xc2A~\x00\xca>\xd3\xb3\xb3I\xd9?\x92\xb9H\xc3\xcbZ\x8a\xf7\\\xff-+\xf6\x19\x82\x89\xdak\xcc.1\xf6\xd4Ns\xa6\x9b\xe0O\xd2\xf2\x9cmC\x01\xdc\xe1\xf5\xb2J\x80'

        self.c_nodeid = 1
        self.c_ip = "127.0.0.1"
        self.c_port = "11112"
        self.c_priv = b'\x8a\x7fRb\xc1\xbaV/\x86\xf6\x7f]\xb2U|\x91\xb2P\x89\x05\x8f\xcfm\x92\x01\x9ej\xbe\x0bJ\x99\x95d\xdd\xb6\xb0\x00\x12\xd1\x0ep\xbc\xd9\x9e\xd0\xfc\xf7I\xd2&\xd4e\x9a$\xa9\xdb\xbb9\x83=\x03\xbe\xb7-\x80k\x0c5\xf9#\xc3\xaa\xd8\xd9\xc1\xc6vO\xe5\xed\x8b\xeb\x8fn\x83\xe8In\x01\xcb\xe8\x9a`?\x16\xc8:\x97b\x97\x10\xfb\x15\xe0\x97\xfd=8#\xb96B\x81\x1a,O\xd0\xa0i\xd6\xf0m\xc8\xe9\xd1\x05G\x85\xaa\xb9\x82B\x90]\t\xc02\xd4:F\r\xc2\x8b\x13]\x80\xf8$\xe1A\xfeR\x9e\xcb;\t\xaf_\xb2\xff\x8cW\xc4\xcaX\x14\xd6|U\xe1\xfa\xc4\xa1d\xa8&gK\xa2\xef\x7f\xf4H0Aw\xa2\xea\x04\x9c\x0f\x93\xc9\xd6e\x17\xe1\xaei\xba\xafx\xa0P\x0c\x84\xbc\xc4r\xb6\x07u@\x1dN\x0f\xc67c1\xf3\xcc_\x0f\x8b\x80 \xea\x01]\xaf\xd2D\xb0\x10\xd0\xdb\xb8E\x8f\xa9\xda\x97T\x96`\x80\xae\xbd\xeb\xcb\xa5\xd2\xa9^.\x12M\xf7\x81\xbc\xc8\x80\x05n\t/>\xc1\x8b\x04|\x82\xca^G\x15\xa0\x8e\xed\xb1\x7f\x04\x9e\x90u\xf6\xa5Z\x88\x85\x0c\xe16y\xff\xd9fk\x8d#\'\xa2\xec\xa4\x8a1\x89\x85\xc2\x7f8)\\\xa8\x81E\xbf`r\x961\xc1n_\x806K\x06\xb1\xe0p\xc5\x01Bdk\xb9\xd0\xb4\xed}Q^wV\x00\x08\x99\xc147.B y\xa2:\x8f\xb8e\xfd\x8e\x8a&\xaa\xf0C\xa6\xdfUL\x82\xa0\xf9\xac\xa9\xb4;4"\xd9\xb4~\xcda $\x17\x0e\xe0\xfczP?\\\xbe=\xa2\x92\xf3*\xc7\x824`\xbe\xb6)=\x0cw\xe3y\xd0\xe2\x8a\xc0\x03\x1e\x02,W\xbf\xff\xd0\xd5\x1b#|Y5\x9b\\so\xady\xd24\x8e\xc3\t\xff\xc0\xae\xf2]A\x1d\xc7\xb9\xb7b\xae\xfd(\n\x90k\xe3\xe7/\xa4\xf1K\xf0\xc5\x04(\x07\x8cZ\xae\xa3-S\xe3{\t\xccA?\x86\xbf\xfarZ\x10@wsu;)\xfe\x9e\xa7a\xc9Ed\xc3G\x11\x88\xb9\xf8\xe2`g\x8c\xc8\x02\x7f\x11<\x92R\xc9\xb6\xaa\x10\xe2\xff\xbd\xa4P[\xe7T\x00&%\x94\xcc\ry $bH=\x9f\\\xfd\xb9y\x99\x83A\xb3\xb6\xf7\xf7\n\xe5\xbe\x8fc)\'\xfb\xffv\x98\xf7\xfb\xce\xfe\xb7P\xddv2sN\x81\x9fB\xcd\xd72\xae`\xfcy\x9e\tg\xc1\xf7\x82O\xce_\xf3\xba\xd4M=\xfd\xfe\x91j!\x13t\xd2x\xb1\x0e#\'\xafv\x15z&\xa3( J\xd0\x8f\x89j\x066b\xf2S\xc0\x9a\xbe\xe4\xad\xf6\xebT\xcen\x91n\xf5\xd7\xbc\x93\x8d\x03\x89C\x82}\x0c\xd0\xf1)j{\x93P\x01\xd8\xbcI\x0f\xaa\x0c\xe1\x18\xb2\x15\x1b\xe3h\xe7Z\xaa\xcb\xee\x83v\x9f\x94n[\xce\x02BN\xecn\x15\x8b\x9fz\x0e\xa6k\xb3\r\x19\xed\xd1\x89\xdf\xb2\x06\xf77\t\xed\x19\xb9\xe8\xa6@6\x93\x85\xd1\t\x87\xfd\x90\xa4\xfa\xdd\r\xec\xdbg\x9c\xbdH\xfd\x19D\xb8\x1d\xd8\x92\x93\xfam\x975\x01\xdeQ\rp\xbb\x992\xcd\xbc\xda\xd7y\xd2\x91)y\x96x\x18\xb6L\xee\t,~Z\xc0\xcd\xc84B\xf1Of\x18\x1e\nr\xbb\x0b\t5\xcb\xf6y\xdc\xa6S\xa8\xffG9\xbd\x1c0\x93\xc2\xc2l\xd2\xd8G.\xbc1*C\xa2\xe4R\x18\xad\x101\x8d\xd8|\xb9\x1f\xa2\xf2H\xed\xa2\xe76\x97OXv\xe0\x8ek\xd3\xfcy/D`\x12\xe57\xabc4\xc2\\\x0b}\xa2@mdIH}>aM\xeeu\x8b;[\xc5\x7f\xa0Z\x87\xfd\xa3)yb\xa7P\xb1\xb6\xb1\xc14/\xbb\x9b\xd3\x08\x1e\xed\x13\x98\x90\xf5JOZv\xfc>\xd1[\xf5\xea%\xae5\xeb\x0e\xd7\xb6IP\x1f\xbd\xf8\xa0UP\x87\xca\x1e\x1cu\xc0=\xcc\x0e2D\x19\xb8\\T\x01\xd6V"\x1c\\\x07\xf8T4*\x1f\xe2.\xd3\xd0B\xaa\xfd\x84\xc7\xb9\xbd^L;\xc7\xc4^J\xf1\xa7q\xa8lo\xfc\x8a\xb4\x9dX\x94\x1d\xd9B\x1c\x10s\xe1m\n\x16V\xb6ml\xbb\xb7M\x1b\xab\x0b\xc7\x9cjK\xb6QI\x8b@\r\x02\x1exMf\x9c\xfa\x1a\xe4\xda\x7f\xc7#\xad\xdb\x90X\xa9\x13\xca\xb7\xca\x8dsr?\x19\xe8J'
        self.c_pub = b'\xeb\xb9\xec\x97X-9\xf0\x92\x08\x88\xc6\x15X\xd5\x95\xe7^\x83\x90o\x9f\x02]\xf7\xa8\xea\xcc(s\xae\x87\xf3\xfe2\xd7r\xe0M\x9e\x80Qy\x96\xdd\xb3BA\xedD\xe0E\x17\xa4Q\xe6\xe0\xccvX\xe4\xebe\xb0\xe1\x00'

    def test_zmq_rpc(self):
        s = RPCServer(self.logger, self.s_nodeid, self.s_ip, self.s_port, self.s_priv, self.s_pub)
        c = RPCClient(self.logger, self.c_priv, self.c_pub, self.c_nodeid, self.s_ip, self.s_port, self.s_pub)

        original_data = b'TEST DATA'

        for i in range(2):
            loop = asyncio.get_event_loop()
            loop.create_task(s.zmq_run_once())
            future = asyncio.ensure_future(c.send_rpc_ping(original_data), loop=loop)
            loop.run_until_complete(future)
            self.assertEqual(future.result(), original_data)
