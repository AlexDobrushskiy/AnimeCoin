# -*- coding: utf-8 -*-

import multiprocessing
import logging
import sys

from core_modules.blackbox_modules.keys import id_keypair_generation_func
from core_modules.masternode_communication import NodeManager
from core_modules.masternode_discovery import discover_nodes

from client_prototype.cefpython.cefpython import start_cefpython


def initlogging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(' %(asctime)s - ' + __name__ + ' - %(levelname)s - %(message)s')
    consolehandler = logging.StreamHandler()
    consolehandler.setFormatter(formatter)
    logger.addHandler(consolehandler)
    return logger


if __name__ == "__main__":
    basedir = sys.argv[1]

    # discover nodes
    logger = initlogging()

    privkey, pubkey = id_keypair_generation_func()
    nodemanager = NodeManager(logger, privkey, pubkey)
    for settings in discover_nodes(basedir):
        nodemanager.add_masternode(settings["nodeid"], settings["ip"], settings["pyrpcport"], settings["pubkey"],
                                   keytype="file")

    # load tabs for masternodes
    browsers = []
    for settings in discover_nodes(basedir):
        url = "http://%s:%s@%s:%s" % (settings["rpcuser"], settings["rpcpassword"], settings["ip"], settings["pyhttpadmin"])
        p = multiprocessing.Process(target=start_cefpython, args=(settings["nodename"], url))
        p.start()
        browsers.append(p)

    input("Press ENTER to stop browsers")

    for browser in browsers:
        browser.terminate()
