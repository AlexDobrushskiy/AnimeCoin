from django.conf import settings
from django.shortcuts import render, redirect, Http404, HttpResponse


from core.models import pubkey, privkey, rpcclient, call_rpc
from core.forms import IdentityRegistrationForm, SendCoinsForm, ArtworkRegistrationForm, ConsoleCommandForm


def index(request):
    infos = call_rpc(rpcclient.call_masternode("DJANGO_REQ", "DJANGO_RESP", ["get_info"]))

    return render(request, "views/index.tpl", {"infos": infos,
                                               "pastel_basedir": settings.PASTEL_BASEDIR})


def walletinfo(request):
    listunspent, receivingaddress, balance = call_rpc(rpcclient.call_masternode("DJANGO_REQ", "DJANGO_RESP",
                                                                                ["get_wallet_info"]))

    form = SendCoinsForm()
    if request.method == "POST":
        form = SendCoinsForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data["recipient_wallet"]
            amount = form.cleaned_data["amount"]

            ret = call_rpc(rpcclient.call_masternode("DJANGO_REQ", "DJANGO_RESP",
                                                     ["send_to_address", address, amount]))

            if ret is not None:
                form.add_error(None, ret)
            else:
                return redirect("/walletinfo/")

    return render(request, "views/walletinfo.tpl", {"listunspent": listunspent, "receivingaddress": receivingaddress,
                                                    "balance": balance, "form": form})


def identity(request):
    ret = call_rpc(rpcclient.call_masternode("DJANGO_REQ", "DJANGO_RESP", ["get_identities", pubkey]))
    addresses, all_identities, identity_txid, identity_ticket = ret

    form = IdentityRegistrationForm()
    if request.method == "POST":
        form = IdentityRegistrationForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data["address"]
            if address not in addresses:
                form.add_error(None, "Addess does not belong to us!")
            else:
                call_rpc(rpcclient.call_masternode("DJANGO_REQ", "DJANGO_RESP", ["register_identity", address]))
                return redirect("/identity")

    return render(request, "views/identity.tpl", {"addresses": addresses,
                                                  "identity_txid": identity_txid,
                                                  "identity_ticket": identity_ticket, "form": form,
                                                  "all_identities": all_identities})


def portfolio(request):
    resp = "TODO"
    return render(request, "views/portfolio.tpl", {"resp": resp})


def exchange(request):
    results = call_rpc(rpcclient.call_masternode("DJANGO_REQ", "DJANGO_RESP", ["ping_masternodes"]))
    return render(request, "views/exchange.tpl", {"results": results})


def trending(request):
    resp = "TODO"
    return render(request, "views/trending.tpl", {"resp": resp})


def browse(request, txid=""):
    tickets, regticket = call_rpc(rpcclient.call_masternode("DJANGO_REQ", "DJANGO_RESP", ["browse", txid]))

    return render(request, "views/browse.tpl", {"tickets": tickets, "txid": txid, "regticket": regticket})


def register(request):
    form = ArtworkRegistrationForm()

    final_actticket, actticket_txid = None, None

    if request.method == "POST":
        form = ArtworkRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # get the actual image data from the form field
            image_field = form.cleaned_data["image_data"]
            image_data = image_field.read()
            image_name = image_field.name

            actticket_txid, final_actticket = call_rpc(rpcclient.call_masternode("DJANGO_REQ", "DJANGO_RESP",
                                                                                 ["register_image", image_name,
                                                                                  image_data]))

    return render(request, "views/register.tpl", {"form": form, "actticket_txid": actticket_txid,
                                                  "final_actticket": final_actticket})


def console(request):
    form = ConsoleCommandForm()
    output = ""
    if request.method == "POST":
        form = ConsoleCommandForm(request.POST)
        if form.is_valid():
            command = form.cleaned_data["command"].split(" ")

            error, result = call_rpc(rpcclient.call_masternode("DJANGO_REQ", "DJANGO_RESP",
                                                               ["execute_console_command", *command]))
            output = result

    return render(request, "views/console.tpl", {"form": form, "output": output})


def explorer(request, functionality, id=""):
    if functionality == "chaininfo":
        chaininfo = call_rpc(rpcclient.call_masternode("DJANGO_REQ", "DJANGO_RESP", ["explorer_get_chaininfo"]))
        return render(request, "views/explorer_chaininfo.tpl", {"chaininfo": chaininfo})
    elif functionality == "block":
        blockcount, block = call_rpc(rpcclient.call_masternode("DJANGO_REQ", "DJANGO_RESP", ["explorer_get_block", id]))

        if id == "":
            return redirect("/explorer/block/%s" % blockcount)

        if block is None:
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
        transaction = call_rpc(rpcclient.call_masternode("DJANGO_REQ", "DJANGO_RESP", ["explorer_gettransaction", id]))
        if transaction is None:
            raise Http404("Address does not exist")
        return render(request, "views/explorer_transaction.tpl", {"transaction": transaction})
    elif functionality == "address":
        transactions = call_rpc(rpcclient.call_masternode("DJANGO_REQ", "DJANGO_RESP", ["explorer_getaddresses", id]))
        if transactions is None:
            raise Http404("Address does not exist")
        return render(request, "views/explorer_addresses.tpl", {"id": id, "transactions": transactions})
    else:
        return redirect("/")


def chunk(request, chunkid_hex):
    image_data = call_rpc(rpcclient.call_masternode("DJANGO_REQ", "DJANGO_RESP", ["get_chunk", chunkid_hex]))

    if image_data is None:
        raise Http404

    # TODO: set content type properly
    return HttpResponse(image_data, content_type="image/png")
