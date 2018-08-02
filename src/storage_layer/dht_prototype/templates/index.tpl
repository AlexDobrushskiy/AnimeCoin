<html>
<head>
    <title>Welcome to the AnimeCoin Simulator!</title>
</head>
<body>
    Welcome!<br />
    <br />
    <form action="/spawn_node" method="post">
        <input type="submit" value="Spawn Node" />
    </form>
    <br />
    Process list:<br />
    <table>
        {% for k, v in processes.items() %}
            <tr>
                <td>{{ k }} {{ v.name }}</td>
                <td>
                    <form action="/kill_node" method="post">
                        <input type="hidden" name="processid" value="{{ k }}" />
                        <input type="submit" value="Kill" />
                    </form>
                </td>
            </tr>
        {% endfor %}
    </table>

</body>
</html>
