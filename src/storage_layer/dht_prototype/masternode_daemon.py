import logging
import time
import os
import subprocess

import bitcoinrpc

from .masternode_modules.settings import MNDeamonSettings
from .masternode_modules.animecoin_modules.animecoin_keys import animecoin_id_keypair_generation_func
from .masternode_modules.blockchain import BlockChain
from .masternode_modules.blockchain_wrapper import ChainWrapper
from .masternode_modules.masternode_logic import MasterNodeLogic


class MasterNodeDaemon:
    def __init__(self, settings):
        # initialize logging
        self.__initlogging(settings["nodename"])
        self.__logger.debug("Started logger")

        self.__settings = MNDeamonSettings(settings)
        self.__nodeid = settings["nodeid"]
        self.__cmnprocess = None

        # start actual blockchain daemon process
        self.start_cmn()

        # set up BlockChain object
        self.blockchain = self.connect_to_daemon()

        # set up ChainWrapper
        self.chainwrapper = ChainWrapper(self.blockchain)

        # set up logic
        # TODO: do we need the cMN pub/privkey at all?
        # mn_address = self.blockchain.jsonrpc.getaccountaddress("")
        # mn_privkey = self.blockchain.jsonrpc.dumpprivkey(mn_address)
        # self.__logger.debug("loaded address %s with privkey %s" % (mn_address, mn_privkey))

        # load or generate keys
        self.__load_keys()

        # spawn logic
        self.logic = MasterNodeLogic(name="node%s" % self.__nodeid,
                                     logger=self.__logger,
                                     nodeid=str(self.__nodeid),
                                     basedir=self.__settings.basedir,
                                     privkey=self.__privkey,
                                     pubkey=self.__pubkey,
                                     ip=self.__settings.ip,
                                     port=self.__settings.pyrpcport,
                                     chunks=[])

    def __initlogging(self, name):
        self.__logger = logging.getLogger(name)
        self.__logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(' %(asctime)s - ' + name + ' - %(levelname)s - %(message)s')
        consolehandler = logging.StreamHandler()
        consolehandler.setFormatter(formatter)
        self.__logger.addHandler(consolehandler)

    def __load_keys(self):
        # TODO: rethink key generation and audit storage process
        privkeypath = os.path.join(self.__settings.basedir, "config", "private.key")
        pubkeypath = os.path.join(self.__settings.basedir, "config", "public.key")

        if not os.path.isfile(privkeypath) or not os.path.isfile(pubkeypath):
            self.__logger.debug("It seems that public and private keys are not generated, creating them now...")
            self.__privkey, self.__pubkey = animecoin_id_keypair_generation_func()
            with open(privkeypath, "wt") as f:
                f.write(self.__privkey)
            os.chmod(privkeypath, 0o0700)
            with open(pubkeypath, "wt") as f:
                f.write(self.__pubkey)
            os.chmod(pubkeypath, 0o0700)
        else:
            with open(privkeypath) as f:
                self.__privkey = f.read()
            with open(pubkeypath) as f:
                self.__pubkey = f.read()

    def get_masternode_details(self):
        return self.__nodeid, "127.0.0.1", self.__settings.pyrpcport, self.__pubkey

    def start_cmn(self):
        self.__logger.debug("Starting bitcoing daemon on rpcport %s" % self.__settings.rpcport)
        self.__cmnprocess = subprocess.Popen([self.__settings.daemon_binary,
                                              "-rpcuser=%s" % self.__settings.rpcuser,
                                              "-rpcpassword=%s" % self.__settings.rpcpassword,
                                              "-regtest=1",
                                              "-gen=1",
                                              "-genproclimit=1",
                                              "-equihashsolver=tromp",
                                              "-showmetrics=0",
                                              "-listenonion=0",
                                              "-txindex",
                                              "-rpcport=%s" % self.__settings.rpcport,
                                              "-port=%s" % self.__settings.port,
                                              "-server",
                                              "-addresstype=legacy",
                                              "-discover=0",
                                              "-datadir=%s" % self.__settings.datadir])

        # self.__logger.debug("Connecting to %s" % NetWorkSettings.BLOCKCHAIN_SEED_ADDR)
        # self.blockchain.bootstrap(NetWorkSettings.BLOCKCHAIN_SEED_ADDR)

    def stop_cmn(self):
        self.__cmnprocess.terminate()
        self.__cmnprocess.wait()

    def connect_to_daemon(self):
        while True:
            blockchain = BlockChain(user=self.__settings.rpcuser,
                                    password=self.__settings.rpcpassword,
                                    ip=self.__settings.ip,
                                    rpcport=self.__settings.rpcport)
            try:
                blockchain.jsonrpc.getwalletinfo()
            except (ConnectionRefusedError, bitcoinrpc.authproxy.JSONRPCException) as exc:
                self.__logger.debug("Exception %s while getting wallet info, retrying..." % exc)
                time.sleep(0.5)
            else:
                self.__logger.debug("Successfully connected to daemon!")
                break
        return blockchain
