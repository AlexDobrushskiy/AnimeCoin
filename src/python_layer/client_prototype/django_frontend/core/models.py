import os
import asyncio
import logging

from django.conf import settings
from core_modules.zmq_rpc import RPCClient
from core_modules.helpers import get_nodeid_from_pubkey


def initlogging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(' %(asctime)s - ' + "%s - %s" % (__name__, os.getpid()) + ' - %(levelname)s - %(message)s')
    consolehandler = logging.StreamHandler()
    consolehandler.setFormatter(formatter)
    logger.addHandler(consolehandler)
    return logger


# def call_parallel_rpcs(tasks):
#     # get event loop, or start a new one
#     need_new_loop = False
#     try:
#         loop = asyncio.get_event_loop()
#     except RuntimeError:
#         need_new_loop = True
#     else:
#         if loop.is_closed():
#             need_new_loop = True
#
#     if need_new_loop:
#         asyncio.set_event_loop(asyncio.new_event_loop())
#         loop = asyncio.get_event_loop()
#
#     futures = []
#     lookup = {}
#     for identifier, task in tasks:
#         future = asyncio.ensure_future(task, loop=loop)
#         futures.append(future)
#         lookup[future] = identifier
#
#     loop.run_until_complete(asyncio.gather(*futures))
#     results = []
#     for future in futures:
#         results.append((lookup[future], future.result()))
#
#     loop.stop()
#     loop.close()
#     return results


def call_rpc(task):
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

    future = asyncio.ensure_future(task, loop=loop)

    result = loop.run_until_complete(future)

    loop.stop()
    loop.close()
    return result


def call_local_process(*args):
    return call_rpc(rpcclient.call_masternode("DJANGO_REQ", "DJANGO_RESP", args))


logger = initlogging()

# internal keys used for RPC between Django and the backend
__privkey = open(settings.PASTEL_DJANGO_PRIVKEY, "rb").read()
__pubkey = open(settings.PASTEL_DJANGO_PUBKEY, "rb").read()

# trade_pubkey - this is the key the backend uses for trading
pubkey = open(settings.PASTEL_TRADE_PUBKEY, "rb").read()

NODEID = get_nodeid_from_pubkey(pubkey)

# we need the server's nodeid, ip, port, pubkey
rpcclient = RPCClient(settings.PASTEL_NODENUM, __privkey, __pubkey, NODEID, settings.PASTEL_RPC_IP,
                      settings.PASTEL_RPC_PORT, settings.PASTEL_RPC_PUBKEY)
