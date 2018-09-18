{% extends "views/base.tpl" %}

{% import "macros.tpl" as macros %}


{% block body %}
<div class="row">
    <div class="col-sm-12 mt-3">
        {% for account, info in accounts.items() %}
            {% set address = info[0] %}
            {% set balance = info[1] %}
            {% set transactions = info[2] %}

            <h2 class="text-info">Address: {{ address }} </h2>
            <h3 class="text-info">Confirmed Balance: {{ balance }}</h3>

    </div>
</div>

<div class="row">
    <div class="col-sm-12 mt-3">
            <h4>Send coins:</h4>
            <form method="post">
                <input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf_token }}" />
                {{ form }}
                <button type="submit" class="btn btn-danger btn-center">Send</button>
            </form>
    </div>
</div>

<div class="row">
    <div class="col-sm-12 mt-3">
            <h4>Transactions:</h4>
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
