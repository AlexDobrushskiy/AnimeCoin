import time
import logging
import signal
import asyncio
import sys
import os
import multiprocessing

from datetime import datetime as dt, timedelta as td

from dht_prototype.masternode_modules.zmq_rpc import RPCException
from dht_prototype.masternode_daemon import MasterNodeDaemon
from dht_prototype.masternode_modules.masternode_communication import NodeManager
from dht_prototype.masternode_modules.masternode_discovery import discover_nodes
from dht_prototype.masternode_modules.animecoin_modules.animecoin_keys import animecoin_id_keypair_generation_func


def test_store_and_retrieve_data(srcnode, dstnode):
    testdata = b'THIS IS TEST DATA'

    # nodes[0].chainwrapper.generate(100)
    txid = srcnode.chainwrapper.store_ticket(testdata)

    # mine a block
    # srcnode.chainwrapper.generate(1)

    resp = dstnode.chainwrapper.retrieve_ticket(txid)
    assert(testdata == resp)


class Simulator:
    def __init__(self, configdir):
        self.__name = "spawner"
        self.__logger = self.__initlogging()
        self.__configdir = configdir

        # generate our keys for RPC
        self.__privkey, self.__pubkey = animecoin_id_keypair_generation_func()

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

    def spawn_masternode(self, settings):
        self.__logger.debug("Starting masternode: %s" % settings["nodeid"])
        mn = MasterNodeDaemon(settings=settings)
        mn.run_event_loop()
        self.__logger.debug("Stopped spawned masternode: %s" % settings["nodeid"])

    def start_masternode_in_new_process(self, settings_list):
        masternodes = {}
        for settings in settings_list:
            os.makedirs(settings["basedir"], exist_ok=True)
            os.makedirs(os.path.join(settings["basedir"], "config"), exist_ok=True)

            p = multiprocessing.Process(target=self.spawn_masternode, args=(settings,))
            p.start()

            nodename = settings["nodename"]
            masternodes[nodename] = p
            self.__logger.debug("Found masternode %s!" % nodename)

            # if len(masternodes) > 1:
            #     self.__logger.debug("ABORTING EARLY")
            #     break

        return masternodes

    def main(self):
        # spawn MasterNode Daemons
        settings_list = discover_nodes(regtestdir)
        masternodes = self.start_masternode_in_new_process(settings_list)

        # connect to animecoinds spawned by daemons
        for settings in discover_nodes(self.__configdir):
            self.__nodemanager.add_masternode(settings["nodeid"], settings["ip"], settings["pyrpcport"],
                                              settings["pubkey"])

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
