import logging

from django.conf import settings
from core_modules.blockchain import BlockChain
from core_modules.chainwrapper import ChainWrapper
from core_modules.masternode_communication import NodeManager
from core_modules.masternode_discovery import read_settings_file


def initlogging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(' %(asctime)s - ' + __name__ + ' - %(levelname)s - %(message)s')
    consolehandler = logging.StreamHandler()
    consolehandler.setFormatter(formatter)
    logger.addHandler(consolehandler)
    return logger


def get_blockchain():
    x = read_settings_file(settings.PASTEL_BASEDIR)
    blockchainsettings = [x["rpcuser"], x["rpcpassword"], x["ip"], x["rpcport"]]
    return BlockChain(*blockchainsettings)


def get_chainwrapper(blockchain):
    return ChainWrapper(blockchain)


logger = initlogging()

privkey = open(settings.PASTEL_PRIVKEY, "rb").read()
pubkey = open(settings.PASTEL_PUBKEY, "rb").read()

# TODO: remove this hack
import os
PASTEL_TEST_NODES_DIR = os.path.dirname(settings.PASTEL_BASEDIR)
nodemanager = NodeManager(logger, privkey, pubkey, PASTEL_TEST_NODES_DIR)
