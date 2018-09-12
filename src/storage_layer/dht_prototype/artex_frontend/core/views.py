from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect

from dht_prototype.masternode_modules.blockchain import BlockChain


def index(request):
    return render(request, "views/index.tpl", {})


def walletinfo(request):
    blockchain = BlockChain("rt", "rt", "127.0.0.1", 12218)
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


def explorer(request):
    resp = "TODO"
    return render(request, "views/explorer.tpl", {"resp": resp})
