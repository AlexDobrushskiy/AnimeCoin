{% extends "views/base.tpl" %}

{% import "macros.tpl" as macros %}


{% block body %}
<div class="row">
    <div class="col-sm-12">
        <h3><a href="/artwork/{{ artid }}">Share url</a></h3>
    </div>

    <div class="col-sm-2 mt-3">
        <h3>Owners</h3>
        <table class="table table-striped">
            <tr>
                <td>
                    <img width="169" height="240" src="/chunk/{{ art_ticket["thumbnailhash"].hex() }}" />
                </td>
            </tr>
            <tr>
                <td>
                    <a href="/download/{{ artid }}">Download</a>
                </td>
            </tr>
            {% for owner, copies in art_owners.items() %}
                <tr>
                    <td>
                        <abbr title="{{ owner.hex() }}">owner: {{ owner.hex()|truncate(17) }}</abbr><br />
                        copies: {{ copies }}
                    </td>
                </tr>
            {% endfor %}
        </table>
    </div>

    <div class="col-sm-8 mt-3">
        <ul class="nav nav-tabs" id="myTab" role="tablist">
            <li class="nav-item">
                <a class="nav-link active" id="home-tab" data-toggle="tab" href="#mytrades" role="tab" aria-controls="mytrades" aria-selected="true">My trades</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" id="profile-tab" data-toggle="tab" href="#opentickets" role="tab" aria-controls="opentickets" aria-selected="false">Open Tickets</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" id="profile-tab" data-toggle="tab" href="#closedtickets" role="tab" aria-controls="closedtickets" aria-selected="false">Closed Tickets</a>
            </li>
        </ul>

        <div class="tab-content" id="myTabContent">
            <div class="tab-pane fade show active" id="mytrades" role="tabpanel" aria-labelledby="mytrades-tab">
                <div class="row">
                    {% for created, txid, valid, status, tickettype, ticket in my_trades %}
                        <div class="col-sm-3 mx-2 my-2 bg-light border border-primary">
                            {{ macros.render_trade(created, txid, valid, status, tickettype, ticket, csrf_token) }}
                        </div>
                    {% endfor %}
                </div>
            </div>


            <div class="tab-pane fade" id="opentickets" role="tabpanel" aria-labelledby="opentickets-tab">
                <div class="row">
                    {% for created, txid, valid, status, tickettype, ticket in open_tickets %}
                        <div class="col-sm-3 mx-2 my-2 bg-light border border-primary">
                            {{ macros.render_trade(created, txid, valid, status, tickettype, ticket, csrf_token) }}
                        </div>
                    {% endfor %}
                </div>
            </div>

            <div class="tab-pane fade" id="closedtickets" role="tabpanel" aria-labelledby="closedtickets-tab">
                {% for created, txid, valid, status, tickettype, ticket in closed_tickets %}
                    <div class="col-sm-3 mx-2 my-2 bg-light border border-primary">
                        {{ macros.render_trade(created, txid, valid, status, tickettype, ticket, csrf_token) }}
                    </div>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
