{% extends "views/base.tpl" %}

{% import "macros.tpl" as macros %}


{% block body %}
<div class="row">
    <div class="col-sm-12">
        <p>My pubkey: {{ pubkey.hex() }}</p>
    </div>
    <div class="col-sm-4 mt-3">
        <h2>Transfer</h2>
        <form method="post" action="/trading/transfer">
            <input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf_token }}" />
            <table class="table">
                {{ transferform }}
            </table>
            <button type="submit" class="btn btn-success btn-center">Transfer artwork</button>
        </form>
    </div>

    <div class="col-sm-4 mt-3">
        <h2>Trade</h2>
        <form method="post" action="/trading/trade">
            <input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf_token }}" />
            <table class="table">
                {{ tradeform }}
            </table>
            <button type="submit" class="btn btn-success btn-center">Trade artwork</button>
        </form>
    </div>

    <div class="col-sm-12 mt-3">
        <p>My artworks</p>
        <table class="table table-striped">
            {% for artid, copies in my_artworks %}
                <tr>
                    <td>
                        artwork: <a href="/artwork/{{ artid.hex() }}">{{ artid.hex() }}</a><br />
                        {{ copies }}
                    </td>
                </tr>
            {% endfor %}
        </table>
    </div>
</div>
{% endblock %}
