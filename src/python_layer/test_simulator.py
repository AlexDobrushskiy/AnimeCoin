import itertools
import time
import logging
import signal
import asyncio
import sys
import os
import multiprocessing

from bitcoinrpc.authproxy import JSONRPCException

from masternode_prototype.masternode_daemon import MasterNodeDaemon
from core_modules.masternode_communication import NodeManager
from core_modules.masternode_discovery import discover_nodes
from core_modules.blackbox_modules.keys import id_keypair_generation_func
from core_modules.blockchain import BlockChain
from core_modules.helpers import require_true


def test_store_and_retrieve_data(srcnode, dstnode):
    testdata = b'THIS IS TEST DATA'

    # nodes[0].chainwrapper.generate(100)
    txid = srcnode.chainwrapper.store_ticket(testdata)

    # mine a block
    # srcnode.chainwrapper.generate(1)

    resp = dstnode.chainwrapper.retrieve_ticket(txid)
    require_true(testdata == resp)


class Simulator:
    def __init__(self, configdir):
        self.__name = "spawner"
        self.__logger = self.__initlogging()
        self.__configdir = configdir

        # generate our keys for RPC
        self.__privkey, self.__pubkey = id_keypair_generation_func()

        # get node manager
        self.__nodemanager = NodeManager(self.__logger, self.__privkey, self.__pubkey)

    def __initlogging(self):
        logger = logging.getLogger(self.__name)
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(' %(asctime)s - ' + self.__name + ' - %(levelname)s - %(message)s')
        consolehandler = logging.StreamHandler()
        consolehandler.setFormatter(formatter)
        logger.addHandler(consolehandler)
        return logger

    def spawn_masternode(self, settings, addnodes):
        self.__logger.debug("Starting masternode: %s" % settings["nodeid"])
        mn = MasterNodeDaemon(settings=settings, addnodes=addnodes)
        mn.run_event_loop()
        self.__logger.debug("Stopped spawned masternode: %s" % settings["nodeid"])

    def start_masternode_in_new_process(self, settings_list, addnodes):
        masternodes = {}
        for settings in settings_list:
            os.makedirs(settings["basedir"], exist_ok=True)
            os.makedirs(os.path.join(settings["basedir"], "config"), exist_ok=True)

            p = multiprocessing.Process(target=self.spawn_masternode, args=(settings, addnodes))
            p.start()

            nodename = settings["nodename"]
            masternodes[nodename] = p
            self.__logger.debug("Found masternode %s!" % nodename)

            # if len(masternodes) > 1:
            #     self.__logger.debug("ABORTING EARLY")
            #     break

        return masternodes

    def __reconnect_masternodes(self, settings_list, waitforboot=True):
        # connect masternodes to each other
        # TODO: there has to be another way where the testnet can take care of this for us
        for nodea, nodeb in itertools.combinations(settings_list, 2):
            newnode = "%s:%s" % (nodeb["ip"], nodeb["port"])
            self.__logger.debug("Adding %s to node %s" % (newnode, nodea["nodeid"]))
            while True:
                try:
                    blockchain = BlockChain(nodea["rpcuser"], nodea["rpcpassword"], nodea["ip"],
                                            nodea["rpcport"])
                    blockchain.jsonrpc.addnode(newnode, "onetry")
                except (JSONRPCException, ConnectionRefusedError) as exc:
                    if waitforboot:
                        self.__logger.debug("Waiting for MasterNode to boot up, exception: %s" % exc)
                        time.sleep(0.5)
                    else:
                        self.__logger.debug("Node went away with exception: %s" % exc)
                        break
                else:
                    self.__logger.debug("Successfully added %s to node %s" % (newnode, nodea["nodeid"]))
                    break

            self.__nodemanager.add_masternode(nodea["nodeid"], nodea["ip"], nodea["pyrpcport"],
                                              nodea["pubkey"], keytype="file")

    def main(self):
        # spawn MasterNode Daemons
        settings_list = discover_nodes(self.__configdir)
        addnodes = ["%s:%s" % (x["ip"], x["port"]) for x in settings_list]
        masternodes = self.start_masternode_in_new_process(settings_list, addnodes)

        # connect to blockchain spawned by daemons
        for settings in settings_list:
            self.__nodemanager.add_masternode(settings["nodeid"], settings["ip"], settings["pyrpcport"],
                                              settings["pubkey"], keytype="file")

        # start our event loop
        loop = asyncio.get_event_loop()
        loop.add_signal_handler(signal.SIGTERM, loop.stop)
        loop.add_signal_handler(signal.SIGINT, loop.stop)

        # run loop until Ctrl-C
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            loop.stop()

        # clean up
        for nodeid, mn in masternodes.items():
            self.__logger.debug("Stopping MN %s" % nodeid)
            if mn.is_alive():
                os.kill(mn.pid, signal.SIGTERM)

        while any([mn.is_alive() for mn in masternodes.values()]):
            self.__logger.debug("Waiting for MNs to stop")
            time.sleep(0.5)

        self.__logger.debug("Stopped, you may press Ctrl-C again")


if __name__ == "__main__":
    regtestdir = sys.argv[1]

    simulator = Simulator(configdir=regtestdir)
    simulator.main()
