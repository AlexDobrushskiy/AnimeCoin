{% extends "views/base.tpl" %}

{% import "macros.tpl" as macros %}


{% block body %}
<div class="row">
    <div class="col-sm-12 mt-3">
        <h1>Browse: {{ resp }}</h1>
        <table class="table">
            {% for txid, ticket in tickets %}
            <tr>
                <td>Ticket</td>
                <td>{{ txid }}</td>
                <td>{{ ticket|pprint }}</td>
                <td>{{ ticket.to_dict()|pprint }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</div>
{% endblock %}
