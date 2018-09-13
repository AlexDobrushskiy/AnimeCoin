{% extends "views/base.tpl" %}

{% import "macros.tpl" as macros %}


{% block body %}
<div class="row">
    <div class="col-sm-12 mt-3">
        <h1>Welcome to artex</h1>
        {% for mn in nodemanager.get_all() %}
            {{ mn }}
        {% endfor %}
    </div>
</div>
{% endblock %}
