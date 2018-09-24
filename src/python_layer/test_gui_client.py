# -*- coding: utf-8 -*-

import multiprocessing
import logging
import sys

from masternode_protype.masternode_modules.animecoin_modules.animecoin_keys import animecoin_id_keypair_generation_func
from masternode_protype.masternode_modules.masternode_communication import NodeManager
from masternode_protype.masternode_modules.masternode_discovery import discover_nodes

from gui_client.cefpython.cefpython import start_cefpython


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

    # discover animecoin nodes
    logger = initlogging()

    privkey, pubkey = animecoin_id_keypair_generation_func()
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
