{% extends "views/base.tpl" %}

{% import "macros.tpl" as macros %}


{% block body %}
<div class="row">
    <div class="col-sm-12 mt-3">
        <h1>Browse:</h1>
        {% if txid == "" %}
            <table class="table">
                {% for txid, ticket in tickets %}
                <tr>
                    <td>Ticket</td>
                    <td><a href="/browse/{{ txid }}">{{ txid }}</a></td>
                    <td>{{ ticket|pprint }}</td>
                    <td>{{ ticket["artist_name"] }}</td>
                    <td>{{ ticket["artwork_title"] }}</td>
                    <td>{{ ticket["total_copies"] }}</td>
                    <td>{{ ticket["imagedata_hash"] }}</td>
                </tr>
                {% endfor %}
            </table>
        {% else %}
            <h5>regticket: {{ regticket }}</h5>
            <p><a href="/chunk/{{ regticket["thumbnailhash"].hex() }}">{{ regticket["thumbnailhash"].hex() }}</a></p>
            <img src="/chunk/{{ regticket["thumbnailhash"].hex() }}" />
            {# <table>
                {% for i in regticket.lubyhashes %}
                    <tr><td>{{ i }}</td></tr>
                {% endfor %}
            </table> #}
        {% endif %}
    </div>
</div>
{% endblock %}
