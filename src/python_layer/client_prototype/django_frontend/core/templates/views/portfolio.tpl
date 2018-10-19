{% extends "views/base.tpl" %}

{% import "macros.tpl" as macros %}


{% block body %}
<div class="row">
    <div class="col-sm-12 mt-3">
        <p>My pubkey: {{ pubkey.hex() }}</p>
        <form method="post">
            <input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf_token }}" />
            <table class="table">
                {{ form }}
            </table>
            <button type="submit" class="btn btn-success btn-center">Transfer artwork</button>
        </form>
    </div>

    <div class="col-sm-12 mt-3">
        <table class="table table-striped">
            {% for artid, copies in resp %}
                <tr>
                    <td>
                        artwork: <a href="/portfolio/{{ artid.hex() }}">{{ artid.hex() }}</a><br />
                        {{ copies }}
                    </td>
                </tr>
            {% endfor %}
        </table>
    </div>
</div>
{% endblock %}
