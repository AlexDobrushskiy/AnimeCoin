{% extends "views/base.tpl" %}

{% import "macros.tpl" as macros %}


{% block body %}
<div class="row">
    <div class="col-sm-3 mt-3">
        {% for info in accounts.values() %}
            {% set address = info[0] %}
            {% set balance = info[1] %}
            {% set transactions = info[2] %}

            <p class="text-info">Address: {{ address }} </p>
            <p class="text-info">Confirmed Balance: {{ balance }}</p>
        {% endfor %}

    </div>

    <div class="col-sm-3 mt-3">
            <h4>Send coins:</h4>
            <form method="post">
                <input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf_token }}" />
                <table class="table">
                    {{ form }}
                </table>
                <button type="submit" class="btn btn-danger btn-center">Send</button>
            </form>
    </div>

    <div class="col-sm-3 mt-3">
            <h4>My Artex Identity</h4>
            {% if identity == none %}
                Your identity is not yet established!
                <form method="post">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf_token }}" />
                    <table class="table">
                        {{ form }}
                    </table>
                    <button type="submit" class="btn btn-danger btn-center">Send</button>
                </form>
            {% else %}
                {{ identity }}
            {% endif %}
    </div>
</div>

<div class="row">
    <div class="col-sm-3 mt-3">
        {% for info in accounts.values() %}
            {% set address = info[0] %}
            {% set balance = info[1] %}
            {% set transactions = info[2] %}

            <h4>Transactions for {{ address }}:</h4>
            <table class="table">
                <thead>
                    <tr>
                        <th>address</th>
                        <th>category</th>
                        <th>amount</th>
                        <th>confirmations</th>
                        <th>blocktime</th>
                        <th>txid</th>
                    </tr>
                </thead>
                <tbody>
                    {% for transaction in transactions %}
                        <tr>
                            <td>{{ macros.render_address_link(transaction["address"]) }}</td>
                            <td>{{ transaction["category"] }}</td>
                            <td>{{ transaction["amount"] }}</td>
                            <td>{{ transaction["confirmations"] }}</td>
                            <td>{{ transaction["blocktime"] }}</td>
                            <td>{{ macros.render_transaction_link(transaction["txid"]) }}</td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% endfor %}
        </p>
    </div>
</div>
{% endblock %}
