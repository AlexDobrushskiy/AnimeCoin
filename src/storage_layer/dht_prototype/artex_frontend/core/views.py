import asyncio
import pprint
from bitcoinrpc.authproxy import JSONRPCException

from django.conf import settings
from django.shortcuts import render, redirect, Http404
from django.http import HttpResponse, HttpResponseRedirect

from core.models import blockchainsettings

from dht_prototype.masternode_modules.blockchain import BlockChain


def index(request):
    # masternodes = nodemanager.get_all()
    #
    # new_loop = asyncio.new_event_loop()
    #
    # results = []
    # for mn in masternodes:
    #     result = new_loop.run_until_complete(mn.send_rpc_ping(b'PING'))
    #     results.append((str(mn), result))
    #
    # new_loop.stop()
    results = ["N/A"]

    return render(request, "views/index.tpl", {"results": results, "animecoin_basedir": settings.ANIMECOIN_BASEDIR})


def walletinfo(request):
    blockchain = BlockChain(*blockchainsettings)
    accounts = {}
    for accountname in blockchain.jsonrpc.listaccounts():
        address = blockchain.jsonrpc.getaccountaddress(accountname)
        balance = blockchain.jsonrpc.getbalance(accountname)
        transactions = blockchain.jsonrpc.listtransactions(accountname)
        accounts[accountname] = address, balance, transactions
    resp = blockchain.jsonrpc.getwalletinfo()
    balance = int(resp["balance"])
    unconfirmed = int(resp["unconfirmed_balance"])
    immature = int(resp["immature_balance"])
    return render(request, "views/walletinfo.tpl", {"accounts": accounts, "balance": balance,
                                                    "unconfirmed": unconfirmed, "immature": immature})


def portfolio(request):
    resp = "TODO"
    return render(request, "views/portfolio.tpl", {"resp": resp})


def exchange(request):
    resp = "TODO"
    return render(request, "views/exchange.tpl", {"resp": resp})


def trending(request):
    resp = "TODO"
    return render(request, "views/trending.tpl", {"resp": resp})


def browse(request):
    resp = "TODO"
    return render(request, "views/browse.tpl", {"resp": resp})


def register(request):
    resp = "TODO"
    return render(request, "views/register.tpl", {"resp": resp})


def explorer(request, functionality, id=""):
    blockchain = BlockChain("rt", "rt", "127.0.0.1", 12218)
    if functionality == "chaininfo":
        chaininfo = blockchain.jsonrpc.getblockchaininfo()
        return render(request, "views/explorer_chaininfo.tpl", {"chaininfo": chaininfo})
    elif functionality == "block":
        blockcount = int(blockchain.jsonrpc.getblockcount())-1
        if id == "":
            return redirect("/explorer/block/%s" % blockcount)

        try:
            block = blockchain.jsonrpc.getblock(id)
        except JSONRPCException:
            raise Http404("Block does not exist")

        # we need a paginator min and max

        if type(id) == str:
            blocknum = int(block["height"])
        else:
            blocknum = int(id)

        pages = (max(0, blocknum-5), min(blocknum+5+1, blockcount+1))
        return render(request, "views/explorer_block.tpl", {"block": block,
                                                            "blocknum": blocknum,
                                                            "pages": pages,
                                                            "blockcount": blockcount})
    elif functionality == "transaction":
        try:
            if id == "":
                transaction = blockchain.jsonrpc.listsinceblock()["transactions"][-1]
            else:
                transaction = blockchain.jsonrpc.gettransaction(id)
        except JSONRPCException:
            raise Http404("Transaction does not exist")
        return render(request, "views/explorer_transaction.tpl", {"transaction": transaction})
    elif functionality == "address":
        try:
            if id != "":
                transactions = blockchain.jsonrpc.listunspent(1, 999999999, [id])
            else:
                transactions = blockchain.jsonrpc.listunspent(1, 999999999)
        except JSONRPCException:
            raise Http404("Address does not exist")
        return render(request, "views/explorer_addresses.tpl", {"id": id, "transactions": transactions})
    else:
        return redirect("/")
