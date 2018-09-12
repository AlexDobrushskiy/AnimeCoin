{% macro render_blockchain_link(id) %}
    <a href="/explorer/block/{{ id }}">{{ id }}</a>
{% endmacro %}

{% macro render_transaction_link(id) %}
    <a href="/explorer/transaction/{{ id }}">{{ id }}</a><br />
{% endmacro %}

{% macro render_address_link(id) %}
    <a href="/explorer/address/{{ id }}">{{ id }}</a><br />
{% endmacro %}
