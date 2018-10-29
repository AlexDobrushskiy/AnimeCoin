{% extends "views/base.tpl" %}

{% import "macros.tpl" as macros %}


{% block body %}
<div class="row">
    <div class="col-sm-12">
        <p>My pubkey: {{ pubkey.hex() }}</p>
    </div>
    <div class="col-sm-4 mt-3">
        <h2>Transfer</h2>
        <form method="post" action="/trading/transfer">
            <input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf_token }}" />
            <table class="table">
                {{ transferform }}
            </table>
            <button type="submit" class="btn btn-success btn-center">Transfer artwork</button>
        </form>
    </div>

    <div class="col-sm-4 mt-3">
        <h2>Trade</h2>
        <form method="post" action="/trading/trade">
            <input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf_token }}" />
            <table class="table">
                {{ tradeform }}
            </table>
            <button type="submit" class="btn btn-success btn-center">Trade artwork</button>
        </form>
    </div>

    <div class="col-sm-12 mt-3">
        <p>My artworks</p>
        <table class="table table-striped">
            {% for artid, copies in my_artworks %}
                <tr>
                    <td>
                        artwork: <a href="/portfolio/artwork/{{ artid.hex() }}">{{ artid.hex() }}</a><br />
                        {{ copies }}
                    </td>
                </tr>
            {% endfor %}
        </table>
    </div>

    <div class="col-sm-12 mt-3">
        <p>My trades</p>
        <table class="table table-striped">
            {% for created, txid, valid, status, tickettype, ticket in my_trades %}
                <tr>
                    <td>
                        created: {{ created }}<br />
                        txid: <a href="/browse/{{ txid }}">{{ txid }}</a><br />
                        type: {{ tickettype }}<br />
                        done: {{ valid }}<br />
                        status: {{ status }}<br />
                        ticket: vvvvvvvvvvvvvvvvvvvvvvv<br />
                        copies: {{ ticket["copies"] }}<br />
                        expiration: {{ ticket["expiration"] }}<br />
                        imagedata_hash: {{ ticket["imagedata_hash"].hex() }}<br />
                        price: {{ ticket["price"] }}<br />
                        public_key: {{ ticket["public_key"].hex() }}<br />
                        type: {{ ticket["type"] }}<br />
                        wallet_address: {{ ticket["wallet_address"] }}<br />

                        {% if status == "locked" %}
                            <form method="post" action="/trading/consummate">
                                <input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf_token }}" />
                                <table class="table">
                                    <input type="hidden" name="txid" value="{{ txid }}" />
                                </table>
                                <button type="submit" class="btn btn-success btn-center">Consummate</button>
                            </form>
                        {% endif %}
                    </td>
                </tr>
            {% endfor %}
        </table>
    </div>
</div>
{% endblock %}
