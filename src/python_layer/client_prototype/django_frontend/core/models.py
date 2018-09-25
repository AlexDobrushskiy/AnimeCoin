import logging

from django.conf import settings
from core_modules.chainwrapper import ChainWrapper
from core_modules.masternode_discovery import read_settings_file
from core_modules.blockchain import BlockChain


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

# ["rt", "rt", "127.0.0.1", 12218]
privkey = open(settings.PASTEL_PRIVKEY).read()
pubkey = open(settings.PASTEL_PUBKEY).read()
