import os
import asyncio
import logging

from django.conf import settings
from core_modules.blockchain import BlockChain
from core_modules.chainwrapper import ChainWrapper
from core_modules.helpers import get_nodeid_from_pubkey
from core_modules.masternode_communication import NodeManager
from core_modules.masternode_discovery import read_settings_file
from core_modules.chunkmanager_modules.aliasmanager import AliasManager


def initlogging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(' %(asctime)s - ' + "%s - %s" % (__name__, os.getpid()) + ' - %(levelname)s - %(message)s')
    consolehandler = logging.StreamHandler()
    consolehandler.setFormatter(formatter)
    logger.addHandler(consolehandler)
    return logger


def get_blockchain():
    x = read_settings_file(settings.PASTEL_BASEDIR)
    blockchainsettings = [x["rpcuser"], x["rpcpassword"], x["ip"], x["rpcport"]]
    return BlockChain(*blockchainsettings)


def get_chainwrapper(blockchain):
    return ChainWrapper(-1, blockchain)


def call_parallel_rpcs(tasks):
    # get event loop, or start a new one
    need_new_loop = False
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        need_new_loop = True
    else:
        if loop.is_closed():
            need_new_loop = True

    if need_new_loop:
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()

    futures = []
    lookup = {}
    for identifier, task in tasks:
        future = asyncio.ensure_future(task, loop=loop)
        futures.append(future)
        lookup[future] = identifier

    loop.run_until_complete(asyncio.gather(*futures))
    results = []
    for future in futures:
        results.append((lookup[future], future.result()))

    loop.stop()
    loop.close()
    return results


logger = initlogging()

privkey = open(settings.PASTEL_PRIVKEY, "rb").read()
pubkey = open(settings.PASTEL_PUBKEY, "rb").read()

# TODO: remove this hack
NODENUM = int(os.path.basename(settings.PASTEL_BASEDIR).lstrip("node"))
NODEID = get_nodeid_from_pubkey(pubkey)

nodemanager = NodeManager(NODENUM, privkey, pubkey)
nodemanager.update_masternode_list()

aliasmanager = AliasManager(NODENUM, NODEID, nodemanager)
