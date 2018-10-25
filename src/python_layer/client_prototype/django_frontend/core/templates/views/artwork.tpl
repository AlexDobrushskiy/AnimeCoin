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
            {% for txid, valid, tickettype, ticket in trade_tickets %}
                <tr>
                    <td>
                        txid: <a href="/browse/{{ txid }}">{{ txid }}</a><br />
                        type: {{ tickettype }}<br />
                        valid: {{ valid }}<br />
                        ticket: {{ ticket }}
                    </td>
                </tr>
            {% endfor %}
        </table>
    </div>
</div>
{% endblock %}
