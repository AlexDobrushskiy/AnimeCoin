{% extends "views/base.tpl" %}

{% import "macros.tpl" as macros %}


{% block body %}
<div class="row">
    <div class="col-sm-12 mt-3">
        <h1>Browse:</h1>
        {% if txid == "" %}
            <table class="table">
                <thead>
                    <tr>
                        <th>TXID</th>
                        <th>Type</th>
                        <th>Ticket</th>
                    </tr>
                </thead>
                <tbody>
                    {% for txid, tickettype, ticket in tickets %}
                    <tr>
                        <td><a href="/browse/{{ txid }}">{{ txid }}</a></td>
                        {% if tickettype == "identity" %}
                            <td>ID</td>
                            <td>
                                blockchain_address: {{ ticket["ticket"]["blockchain_address"] }}<br />
                                public_key: {{ ticket["ticket"]["public_key"] }}<br />
                            </td>
                        {% elif tickettype == "regticket" %}
                            <td>Registration</td>
                            <td>
                                {% set artid = ticket['ticket']['imagedata_hash'].hex() %}
                                artist_name: {{ ticket["ticket"]["artist_name"] }}<br />
                                artwork_title: {{ ticket["ticket"]["artwork_title"] }}<br />
                                imagedata_hash: <a href="/portfolio/artwork/{{ artid }}">{{ artid }}</a><br />
                            </td>
                        {% elif tickettype == "actticket" %}
                            <td>Activation</td>
                            <td>
                                author: {{ ticket["ticket"]["author"] }}<br />
                                registration_ticket_txid: {{ ticket["ticket"]["registration_ticket_txid"] }}<br />
                            </td>
                        {% elif tickettype == "transticket" %}
                            <td>Transfer</td>
                            <td>
                                {% set artid = ticket['ticket']['imagedata_hash'].hex() %}
                                image: <a href="/portfolio/artwork/{{ artid }}">{{ artid }}</a><br />
                                copies: {{ ticket["ticket"]["copies"] }}<br />
                                public_key: {{ ticket["ticket"]["public_key"] }}<br />
                                recipient: {{ ticket["ticket"]["recipient"] }}<br />
                            </td>
                        {% elif tickettype == "tradeticket" %}
                            <td>Trade</td>
                            <td>
                                {% set artid = ticket['ticket']['imagedata_hash'].hex() %}
                                type: {{ ticket["ticket"]["type"] }}<br />
                                image: <a href="/portfolio/artwork/{{ artid }}">{{ artid }}</a><br />
                                copies: {{ ticket["ticket"]["copies"] }}<br />
                                price: {{ ticket["ticket"]["price"] }}<br />
                                expiration: {{ ticket["ticket"]["expiration"] }}<br />
                            </td>
                        {% else %}
                            <td>UNKOWN TYPE: {{ tickettype }}</td>
                            <td>{{ ticket|pprint }}</td>
                        {% endif %}
                    </tr>
                </tbody>
                {% endfor %}
            </table>
        {% else %}
            <h5>ticket:</h5>
            <p>{{ ticket|pprint }}</p>
        {% endif %}
    </div>
</div>
{% endblock %}
