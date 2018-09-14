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
    def __init__(self, daemon_binary, configdir):
        self.__name = "spawner"
        self.__logger = self.__initlogging()
        self.__daemon_binary = daemon_binary
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
        mn = MasterNodeDaemon(settings=settings)

        # start async loops
        loop = asyncio.get_event_loop()

        # set signal handlers
        loop.add_signal_handler(signal.SIGTERM, loop.stop)

        loop.create_task(mn.logic.zmq_run_forever())
        # loop.create_task(mn.logic.run_heartbeat_forever())
        # loop.create_task(mn.logic.run_ping_test_forever())
        # loop.create_task(mn.logic.issue_random_tests_forever(1))
        loop.create_task(mn.logic.run_workers_forever())

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            loop.stop()
        mn.stop_cmn()
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

    async def run_heartbeat_forever(self):
        while True:
            # await asyncio.sleep(1)

            data = b'PING'

            mn = self.__nodemanager.get_random()

            start = dt.now()
            try:

                response_data = await mn.send_rpc_ping(data)
                end = dt.now()
            except RPCException as exc:
                self.__logger.info("PING RPC FAILED for node %s with exception %s" % (mn, exc))
            else:
                if response_data != data:
                    self.__logger.warning("PING FAILED for node %s (%s != %s)" % (mn, data, response_data))
                else:
                    self.__logger.debug("PING SUCCESS for node %s for chunk: %s" % (mn, data))

                # TODO: track successes/errors
            elapsed = (dt.now()-start).total_seconds()
            self.__logger.debug("PING took %.2f seconds" % elapsed)

    def main(self):
        # spawn MasterNode Daemons
        settings_list = discover_nodes(path_to_daemon_binary, regtestdir)
        masternodes = self.start_masternode_in_new_process(settings_list)

        # connect to animecoinds spawned by daemons
        for settings in discover_nodes(self.__daemon_binary, self.__configdir):
            self.__nodemanager.add_masternode(settings["nodeid"], settings["ip"], settings["pyrpcport"], settings["pubkey"])

        # start our event loop
        loop = asyncio.get_event_loop()
        loop.add_signal_handler(signal.SIGTERM, loop.stop)
        loop.add_signal_handler(signal.SIGINT, loop.stop)
        loop.create_task(self.run_heartbeat_forever())

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
    path_to_daemon_binary = sys.argv[1]
    regtestdir = sys.argv[2]

    simulator = Simulator(daemon_binary=path_to_daemon_binary, configdir=regtestdir)
    simulator.main()
