import logging

from django.db import models
from django.conf import settings
from dht_prototype.masternode_modules.masternode_communication import NodeManager
from dht_prototype.masternode_modules.masternode_discovery import discover_nodes

from dht_prototype.masternode_modules.animecoin_modules.animecoin_keys import animecoin_id_keypair_generation_func


def initlogging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(' %(asctime)s - ' + __name__ + ' - %(levelname)s - %(message)s')
    consolehandler = logging.StreamHandler()
    consolehandler.setFormatter(formatter)
    logger.addHandler(consolehandler)
    return logger


# discover animecoin nodes
logger = initlogging()

privkey, pubkey = animecoin_id_keypair_generation_func()
nodemanager = NodeManager(logger, privkey, pubkey)
for settings in discover_nodes(settings.ANIMECOIN_NODES_PATH):
    nodemanager.add_masternode(settings["nodeid"], settings["ip"], settings["pyrpcport"], settings["pubkey"])
