import asyncio
import signal
import logging
import time
import os
import subprocess

import bitcoinrpc

from core_modules.logger import initlogging
from core_modules.settings import MNDeamonSettings, NetWorkSettings
from core_modules.blackbox_modules.keys import id_keypair_generation_func
from core_modules.blockchain import BlockChain
from core_modules.chainwrapper import ChainWrapper
from masternode_prototype.masternode_logic import MasterNodeLogic


class MasterNodeDaemon:
    def __init__(self, settings, addnodes=None):
        # initialize logging
        self.__logger = initlogging(int(settings["nodename"]), __name__)
        self.__logger.debug("Started logger")

        self.__settings = MNDeamonSettings(settings)
        self.__addnodes = addnodes
        self.__nodenum = settings["nodeid"]

        # processes
        self.__cmnprocess = None
        self.__djangoprocess = None

        # start actual blockchain daemon process
        self.__start_cmn()

        # start the django process
        self.__start_django()

        # set up BlockChain object
        self.blockchain = self.__connect_to_daemon()

        # set up ChainWrapper
        self.chainwrapper = ChainWrapper(self.__nodenum, self.blockchain)

        # load or generate keys
        self.__load_keys()

        # spawn logic
        self.logic = MasterNodeLogic(nodenum=self.__nodenum,
                                     chainwrapper=self.chainwrapper,
                                     basedir=self.__settings.basedir,
                                     privkey=self.__privkey,
                                     pubkey=self.__pubkey,
                                     ip=self.__settings.ip,
                                     port=self.__settings.pyrpcport,
                                     chunks=[])

    def __load_keys(self):
        # TODO: rethink key generation and audit storage process
        privkeypath = os.path.join(self.__settings.basedir, "config", "private.key")
        pubkeypath = os.path.join(self.__settings.basedir, "config", "public.key")

        if not os.path.isfile(privkeypath) or not os.path.isfile(pubkeypath):
            self.__logger.debug("It seems that public and private keys are not generated, creating them now...")
            self.__privkey, self.__pubkey = id_keypair_generation_func()
            with open(privkeypath, "wb") as f:
                f.write(self.__privkey)
            os.chmod(privkeypath, 0o0700)
            with open(pubkeypath, "wb") as f:
                f.write(self.__pubkey)
            os.chmod(pubkeypath, 0o0700)
        else:
            with open(privkeypath, "rb") as f:
                self.__privkey = f.read()
            with open(pubkeypath, "rb") as f:
                self.__pubkey = f.read()

    def __start_django(self):
        env = os.environ.copy()
        env["PASTEL_BASEDIR"] = self.__settings.datadir

        cmdline = [
            NetWorkSettings.PYTHONPATH,
            "manage.py",
            "runserver",
            str(self.__settings.pyhttpadmin)
        ]

        self.__djangoprocess = subprocess.Popen(cmdline, cwd=NetWorkSettings.DJANGO_ROOT, env=env)

    def __stop_django(self):
        self.__djangoprocess.terminate()
        self.__djangoprocess.wait()

    def __start_cmn(self):
        self.__logger.debug("Starting bitcoing daemon on rpcport %s" % self.__settings.rpcport)
        cmdline = [
            NetWorkSettings.BLOCKCHAIN_BINARY,
            "-rpcuser=%s" % self.__settings.rpcuser,
            "-rpcpassword=%s" % self.__settings.rpcpassword,
            "-testnet=1",
            # "-regtest=1",
            "-dnsseed=0",
            # "-gen=1",
            "-debug=1",
            "-genproclimit=1",
            "-equihashsolver=tromp",
            "-showmetrics=0",
            "-listenonion=0",
            "-onlynet=ipv4",
            "-txindex",
            "-rpcport=%s" % self.__settings.rpcport,
            "-port=%s" % self.__settings.port,
            "-server",
            "-addresstype=legacy",
            "-discover=0",
            "-datadir=%s" % self.__settings.datadir
        ]

        if self.__addnodes is not None:
            for nodeaddress in self.__addnodes:
                self.__logger.debug("Adding extra node %s to cmdline with -addnode" % nodeaddress)
                cmdline.append("-addnode=%s" % nodeaddress)

        self.__cmnprocess = subprocess.Popen(cmdline, cwd=NetWorkSettings.BASEDIR)

    def __stop_cmn(self):
        self.__cmnprocess.terminate()
        self.__cmnprocess.wait()

    def __connect_to_daemon(self):
        while True:
            blockchain = BlockChain(user=self.__settings.rpcuser,
                                    password=self.__settings.rpcpassword,
                                    ip=self.__settings.ip,
                                    rpcport=self.__settings.rpcport)
            try:
                blockchain.getwalletinfo()
            except (ConnectionRefusedError, bitcoinrpc.authproxy.JSONRPCException) as exc:
                self.__logger.debug("Exception %s while getting wallet info, retrying..." % exc)
                time.sleep(0.5)
            else:
                self.__logger.debug("Successfully connected to daemon!")
                break
        return blockchain

    def run_event_loop(self):
        # start async loops
        loop = asyncio.get_event_loop()

        # set signal handlers
        loop.add_signal_handler(signal.SIGTERM, loop.stop)

        loop.create_task(self.logic.zmq_run_forever())
        loop.create_task(self.logic.run_masternode_parser())
        loop.create_task(self.logic.run_ticket_parser())
        # loop.create_task(mn.logic.run_heartbeat_forever())
        # loop.create_task(self.logic.run_ping_test_forever())
        # loop.create_task(mn.logic.issue_random_tests_forever(1))
        loop.create_task(self.logic.run_workers_forever())

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            loop.stop()
        self.__stop_cmn()
        self.__stop_django()
