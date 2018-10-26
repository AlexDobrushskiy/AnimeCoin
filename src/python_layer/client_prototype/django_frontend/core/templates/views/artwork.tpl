{% extends "views/base.tpl" %}

{% import "macros.tpl" as macros %}


{% block body %}
<div class="row">
    <div class="col-sm-12">
        <h3>Artid: {{ artid }}</h3>
    </div>

    <div class="col-sm-12 mt-3">
        <h3>Owners</h3>
        <table class="table table-striped">
            {% for owner, copies in art_owners.items() %}
                <tr>
                    <td>
                        owner: {{ owner.hex() }}<br />
                        copies: {{ copies }}
                    </td>
                </tr>
            {% endfor %}
        </table>
    </div>

    <div class="col-sm-12 mt-3">
        <h3>Tickets</h3>
        <table class="table table-striped">
            {% for created, txid, valid, status, tickettype, ticket in trade_tickets %}
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
                    </td>
                </tr>
            {% endfor %}
        </table>
    </div>
</div>
{% endblock %}
