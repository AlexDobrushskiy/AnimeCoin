from bitcoinrpc.authproxy import JSONRPCException

from django.conf import settings
from django.shortcuts import render, redirect, Http404

from core_modules.masternode_ticketing import ArtRegistrationClient, IDRegistrationClient

from core.models import get_blockchain, get_chainwrapper, pubkey, privkey
from core.forms import IdentityRegistrationForm, SendCoinsForm, ArtworkRegistrationForm, ConsoleCommandForm


def index(request):
    blockchain = get_blockchain()
    infos = {}
    for name in ["getblockchaininfo", "getmempoolinfo", "gettxoutsetinfo", "getmininginfo",
                 "getnetworkinfo", "getpeerinfo", "getwalletinfo"]:
        infos[name] = getattr(blockchain.jsonrpc, name)()

    return render(request, "views/index.tpl", {"infos": infos,
                                               "pastel_basedir": settings.PASTEL_BASEDIR})


def walletinfo(request):
    blockchain = get_blockchain()

    listunspent = blockchain.jsonrpc.listunspent()

    form = SendCoinsForm()
    if request.method == "POST":
        form = SendCoinsForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data["recipient_wallet"]
            amount = form.cleaned_data["amount"]
            try:
                blockchain.jsonrpc.sendtoaddress(address, amount)
            except JSONRPCException as exc:
                form.add_error(None, str(exc))
            else:
                return redirect("/walletinfo/")

    return render(request, "views/walletinfo.tpl", {"listunspent": listunspent,
                                                    "form": form})


def identity(request):
    blockchain = get_blockchain()
    chainwrapper = get_chainwrapper(blockchain)

    addresses = []
    for unspent  in blockchain.jsonrpc.listunspent():
        if unspent["address"] not in addresses:
            addresses.append(unspent["address"])

    identity = chainwrapper.get_identity_ticket(pubkey)
    all_identities = chainwrapper.get_tickets_by_type("identity")

    form = IdentityRegistrationForm()
    if request.method == "POST":
        form = IdentityRegistrationForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data["address"]
            if address not in addresses:
                form.add_error(None, "Addess does not belong to us!")
            else:
                regclient = IDRegistrationClient(privkey, pubkey, chainwrapper)
                regclient.register_id(address)
                return redirect("/identity")

    return render(request, "views/identity.tpl", {"addresses": addresses, "identity": identity, "form": form,
                                                  "all_identities": all_identities})


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
    blockchain = get_blockchain()
    chainwrapper = get_chainwrapper(blockchain)
    identities = chainwrapper.get_tickets_by_type("identity")
    return render(request, "views/browse.tpl", {"identities": identities})


def register(request):
    form = ArtworkRegistrationForm()
    blockchain = get_blockchain()

    if request.method == "POST":
        form = ArtworkRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # get the actual image data from the form field
            image_field = form.cleaned_data["image_data"]
            image_data = image_field.read()

            # get the registration object
            artreg = ArtRegistrationClient(settings.PASTEL_PRIVKEY, settings.PASTEL_PUBKEY, blockchain)

            # register image
            # TODO: fill these out properly
            actticket_txid = artreg.register_image(
                image_data=image_data,
                artist_name="Example Artist",
                artist_website="exampleartist.com",
                artist_written_statement="This is only a test",
                artwork_title="My Example Art",
                artwork_series_name="Examples and Tests collection",
                artwork_creation_video_youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                artwork_keyword_set="example, testing, sample",
                total_copies=10
            )

            # get and process ticket as new node
            # get_ticket_as_new_node(actticket_txid, chainwrapper, chunkstorage)

    return render(request, "views/register.tpl", {"form": form})


def console(request):
    blockchain = get_blockchain()
    form = ConsoleCommandForm()
    output = ""
    if request.method == "POST":
        form = ConsoleCommandForm(request.POST)
        if form.is_valid():
            command = form.cleaned_data["command"].split(" ")
            commandname, args = command[0], command[1:]
            command_rpc = getattr(blockchain.jsonrpc, commandname)
            try:
                result = command_rpc(*args)
            except JSONRPCException as exc:
                output = "EXCEPTION: %s" % exc
            else:
                output = result
    return render(request, "views/console.tpl", {"form": form, "output": output})


def explorer(request, functionality, id=""):
    blockchain = get_blockchain()
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
