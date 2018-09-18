{% extends "views/base.tpl" %}

{% import "macros.tpl" as macros %}


{% block body %}
<div class="row">
    <div class="col-sm-12 mt-3">
        <h1>Browse: {{ resp }}</h1>
        <table class="table">
            {% for identity in identities %}
            <tr>
                <td>Identity</td>
                <td>{{ identity|pprint }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</div>
{% endblock %}
