import os
import subprocess
import time

import bitcoinrpc

from .masternode_modules.animecoin_modules.animecoin_keys import animecoin_id_keypair_generation_func
from .masternode_modules.blockchain import BlockChain, NetWorkSettings
from .masternode_modules.blockchain_wrapper import ChainWrapper
from .masternode_modules.masternode_logic import MasterNodeLogic


class MasterNode:
    def __init__(self, nodeid, settings):
        self.nodeid = "node%s" % nodeid
        self.__settings = settings

        rpcuser = self.__settings["rpcuser"]
        rpcpassword = self.__settings["rpcpassword"]
        rpcport = self.__settings["rpcport"]

        # set up BlockChain object
        self.blockchain = BlockChain(rpcuser, rpcpassword, "127.0.0.1", rpcport)

        # set up ChainWrapper
        self.chainwrapper = ChainWrapper(self.blockchain)

        # set up logic
        # TODO: do we need the cMN pub/privkey at all?
        # mn_address = self.blockchain.jsonrpc.getaccountaddress("")
        # mn_privkey = self.blockchain.jsonrpc.dumpprivkey(mn_address)
        # print("loaded address %s with privkey %s" % (mn_address, mn_privkey))

        # TODO: store these somewhere
        privkey, pubkey = animecoin_id_keypair_generation_func()

        masternode_list = []
        self.__logic = MasterNodeLogic(name="node%s"%self.nodeid,
                                       nodeid=self.nodeid,
                                       basedir=self.__settings["chunkdir"],
                                       privkey=privkey,
                                       pubkey=pubkey,
                                       masternode_list=masternode_list,
                                       chunks=[])

# # Currently unused
# class MasterNodeProcess:
#     def __init__(self, basedir, daemon_binary):
#         self.__basedir = basedir
#         self.__daemon_binary = daemon_binary
#
#         # create blockchain directory if it does not exist
#         self.__blockchaindir = os.path.join(self.__basedir, "blockchain")
#
#         self.__bitcoinprocess = None
#
#         # load settings
#         self.__settings = MasterNodeSettings(self.__basedir)
#
#     def start_bitcoind(self):
#         # TODO refactor settings handling
#         rpcuser = self.__settings.settings["blockchain"]["rpcuser"]
#         rpcpassword = self.__settings.settings["blockchain"]["rpcpassword"]
#         rpcport = self.__settings.settings["blockchain"]["rpcport"]
#         port = self.__settings.settings["blockchain"]["port"]
#
#         # TODO: make this differ between testing and prod
#         print("Starting bitcoing daemon", port)
#         self.__bitcoinprocess = subprocess.Popen([self.__daemon_binary, "-rpcuser=%s" % rpcuser,
#                                                   "-rpcpassword=%s" % rpcpassword, "-testnet", "-gen=1",
#                                                   "-genproclimit=1", "-equihashsolver=tromp", "-showmetrics=0",
#                                                   "-txindex", "-rpcport=%s" % rpcport, "-port=%s" % port,
#                                                   "-server", "-addresstype=legacy", "-discover=0",
#                                                   "-datadir=%s" % self.__blockchaindir])
#
#         # time.sleep(NetWorkSettings.BITCOIN_BOOT_WAIT_TIME)
#         # while True:
#         #     try:
#         #         self.blockchain.jsonrpc.getwalletinfo()
#         #     except bitcoinrpc.authproxy.JSONRPCException as exc:
#         #         print("Exception while getting wallet info, retrying", exc)
#         #         time.sleep(0.5)
#         #     except ConnectionRefusedError:
#         #         # TODO: handle bitcoin client errors more robustly
#         #         raise RuntimeError("Failed to start bitcoin daemon!")
#         #     else:
#         #         break
#         #
#         # print("Connecting to %s" % NetWorkSettings.BLOCKCHAIN_SEED_ADDR)
#         # self.blockchain.bootstrap(NetWorkSettings.BLOCKCHAIN_SEED_ADDR)
#
#     def stop_bitcoind(self):
#         self.__bitcoinprocess.terminate()
#         self.__bitcoinprocess.wait()
