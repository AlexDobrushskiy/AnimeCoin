{% extends "views/base.tpl" %}

{% import "macros.tpl" as macros %}


{% block body %}
<div class="row">
    <div class="col-sm-12 mt-3">
        <h1>Welcome to artex, animecoind dir: {{ animecoin_basedir }}</h1>
        <h5>Network info:</h5>
        <pre>{{ networkinfo|pprint }}</pre>
        {% for result in results %}
            {{ result }}<br />
        {% endfor %}
    </div>
</div>
{% endblock %}
