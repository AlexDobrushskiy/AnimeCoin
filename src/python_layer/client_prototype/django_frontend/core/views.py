import asyncio

from bitcoinrpc.authproxy import JSONRPCException

from django.conf import settings
from django.shortcuts import render, redirect, Http404

from core_modules.masternode_ticketing import ArtRegistrationClient, IDRegistrationClient
from core_modules.helpers import bytes_to_int

from core.models import get_blockchain, get_chainwrapper, pubkey, privkey, nodemanager, call_parallel_rpcs
from core.forms import IdentityRegistrationForm, SendCoinsForm, ArtworkRegistrationForm, ConsoleCommandForm


def index(request):
    blockchain = get_blockchain()
    infos = {}
    for name in ["getblockchaininfo", "getmempoolinfo", "gettxoutsetinfo", "getmininginfo",
                 "getnetworkinfo", "getpeerinfo", "getwalletinfo"]:
        infos[name] = getattr(blockchain, name)()

    infos["mnsync"] = blockchain.mnsync("status")

    return render(request, "views/index.tpl", {"infos": infos,
                                               "pastel_basedir": settings.PASTEL_BASEDIR})


def walletinfo(request):
    blockchain = get_blockchain()

    receivingaddress = blockchain.getaccountaddress("")
    balance = blockchain.getbalance()

    listunspent = blockchain.listunspent()

    form = SendCoinsForm()
    if request.method == "POST":
        form = SendCoinsForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data["recipient_wallet"]
            amount = form.cleaned_data["amount"]
            try:
                blockchain.sendtoaddress(address, amount)
            except JSONRPCException as exc:
                form.add_error(None, str(exc))
            else:
                return redirect("/walletinfo/")

    return render(request, "views/walletinfo.tpl", {"listunspent": listunspent, "receivingaddress": receivingaddress,
                                                    "balance": balance, "form": form})


def identity(request):
    blockchain = get_blockchain()
    chainwrapper = get_chainwrapper(blockchain)

    addresses = []
    for unspent  in blockchain.listunspent():
        if unspent["address"] not in addresses:
            addresses.append(unspent["address"])

    identity_txid, identity_ticket = chainwrapper.get_identity_ticket(pubkey)
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

    return render(request, "views/identity.tpl", {"addresses": addresses,
                                                  "identity_txid": identity_txid,
                                                  "identity_ticket": identity_ticket, "form": form,
                                                  "all_identities": all_identities})


def portfolio(request):
    resp = "TODO"
    return render(request, "views/portfolio.tpl", {"resp": resp})


def exchange(request):
    masternodes = nodemanager.get_all()

    tasks = []
    for mn in masternodes:
        tasks.append((str(mn), mn.send_rpc_ping(b'PING')))
    results = call_parallel_rpcs(tasks)

    return render(request, "views/exchange.tpl", {"results": results})


def trending(request):
    resp = "TODO"
    return render(request, "views/trending.tpl", {"resp": resp})


def browse(request, txid=""):
    blockchain = get_blockchain()
    chainwrapper = get_chainwrapper(blockchain)

    tickets, regticket, lubyhashes = [], None, []
    if txid == "":
        for tmptxid, final_actticket in chainwrapper.get_tickets_by_type("actticket"):
            final_actticket.validate(chainwrapper)
            final_regticket = chainwrapper.retrieve_ticket(final_actticket.ticket.registration_ticket_txid)
            final_regticket.validate(chainwrapper)
            regticket = final_regticket.ticket
            tickets.append((tmptxid, regticket))

    else:
        # get and process ticket as new node
        final_actticket = chainwrapper.retrieve_ticket(txid)
        final_actticket.validate(chainwrapper)
        final_regticket = chainwrapper.retrieve_ticket(final_actticket.ticket.registration_ticket_txid)
        final_regticket.validate(chainwrapper)
        regticket = final_regticket.ticket

        # # fetch chunks - TODO: compute who should have this chunk
        # mn = nodemanager.get_all()[0]
        #
        # tasks = []
        # for chunkid_bytes in regticket.lubyhashes:
        #     chunkid = bytes_to_int(chunkid_bytes)
        #     tasks.append(("%s from %s" % (chunkid, str(mn)), mn.send_rpc_fetchchunk(chunkid)))
        #
        # print("STARTING %s" % len(tasks))
        # results = call_parallel_rpcs(tasks)
        # for result in results:
        #     print("RESULT", result)

        # fetch thumbnail
        mn = nodemanager.get_masternode_ordering(regticket.order_block_txid)[0]

        tasks = []
        chunkid = bytes_to_int(regticket.thumbnailhash)
        tasks.append(("%s from %s" % (chunkid, str(mn)), mn.send_rpc_fetchchunk(chunkid)))

        print("STARTING %s" % len(tasks))
        results = call_parallel_rpcs(tasks)
        for result in results:
            print("RESULT", result)

    return render(request, "views/browse.tpl", {"tickets": tickets, "txid": txid, "regticket": regticket})


def register(request):
    form = ArtworkRegistrationForm()
    chainwrapper = get_chainwrapper(get_blockchain())

    final_actticket, actticket_txid = None, None

    if request.method == "POST":
        form = ArtworkRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # get the actual image data from the form field
            image_field = form.cleaned_data["image_data"]
            image_data = image_field.read()

            # get the registration object
            artreg = ArtRegistrationClient(privkey, pubkey, chainwrapper, nodemanager)

            # register image
            # TODO: fill these out properly
            task = artreg.register_image(
                image_data=image_data,
                artist_name="Example Artist",
                artist_website="exampleartist.com",
                artist_written_statement="This is only a test",
                artwork_title=image_field.name,
                artwork_series_name="Examples and Tests collection",
                artwork_creation_video_youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                artwork_keyword_set="example, testing, sample",
                total_copies=10
            )

            # TODO: this interface is very awkward
            results = call_parallel_rpcs([("dummy", task)])
            actticket_txid = results[0][1]
            final_actticket = chainwrapper.retrieve_ticket(actticket_txid, validate=True)

    return render(request, "views/register.tpl", {"form": form, "actticket_txid": actticket_txid,
                                                  "final_actticket": final_actticket})


def console(request):
    blockchain = get_blockchain()
    form = ConsoleCommandForm()
    output = ""
    if request.method == "POST":
        form = ConsoleCommandForm(request.POST)
        if form.is_valid():
            command = form.cleaned_data["command"].split(" ")
            commandname, args = command[0], command[1:]
            command_rpc = getattr(blockchain, commandname)
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
        chaininfo = blockchain.getblockchaininfo()
        return render(request, "views/explorer_chaininfo.tpl", {"chaininfo": chaininfo})
    elif functionality == "block":
        blockcount = blockchain.getblockcount()-1
        if id == "":
            return redirect("/explorer/block/%s" % blockcount)

        try:
            block = blockchain.getblock(id)
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
                transaction = blockchain.listsinceblock()["transactions"][-1]
            else:
                transaction = blockchain.gettransaction(id)
        except JSONRPCException:
            raise Http404("Transaction does not exist")
        return render(request, "views/explorer_transaction.tpl", {"transaction": transaction})
    elif functionality == "address":
        try:
            if id != "":
                transactions = blockchain.listunspent(1, 999999999, [id])
            else:
                transactions = blockchain.listunspent(1, 999999999)
        except JSONRPCException:
            raise Http404("Address does not exist")
        return render(request, "views/explorer_addresses.tpl", {"id": id, "transactions": transactions})
    else:
        return redirect("/")
