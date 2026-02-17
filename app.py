#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from flask import Flask, request, redirect, url_for, render_template_string
import threading

app = Flask(__name__)

league = ['Trey', 'Hanvey', 'Matt', 'Dakota', 'Tulenko', 'Jacob', 'Joseph', 'Drew']
TOTAL_ROUNDS = 25

ROSTER_TEMPLATE = {
    "QB": 1,
    "RB": 1,
    "WR": 2,
    "TE": 1,
    "Flex (WR/RB/TE)": 1,
    "LT": 1,
    "LG": 1,
    "C": 1,
    "RG": 1,
    "RT": 1,
    "DL": 3,
    "LB": 3,
    "Flex Defense (LB/DL)": 1,
    "DB": 4,
    "Punter": 1,
    "Kicker": 1,
    "Head Coach": 1
}

draft_state = {
    "round": 1,
    "pick_index": 0,
    "teams": {},
    "drafted_players": set(),
    "complete": False
}

lock = threading.Lock()

for user in league:
    draft_state["teams"][user] = {pos: [] for pos in ROSTER_TEMPLATE}


def snake_order(round_number):
    return league if round_number % 2 == 1 else list(reversed(league))


def current_drafter():
    order = snake_order(draft_state["round"])
    return order[draft_state["pick_index"]]


def advance_draft():
    if draft_state["pick_index"] < len(league) - 1:
        draft_state["pick_index"] += 1
    else:
        draft_state["pick_index"] = 0
        draft_state["round"] += 1

    if draft_state["round"] > TOTAL_ROUNDS:
        draft_state["complete"] = True


def valid_position(user, position):
    if position not in ROSTER_TEMPLATE:
        return False
    return len(draft_state["teams"][user][position]) < ROSTER_TEMPLATE[position]


@app.route("/", methods=["GET", "POST"])
def draft():
    user = request.args.get("user")
    message = ""

    if user not in league:
        return "Invalid user. Add ?user=YourName to URL."

    with lock:
        if request.method == "POST" and not draft_state["complete"]:
            if user != current_drafter():
                message = "Not your turn."
            else:
                player = request.form["player"].strip()
                position = request.form["position"].strip()

                if player in draft_state["drafted_players"]:
                    message = f"{player} is not available."
                elif not valid_position(user, position):
                    message = "Invalid or filled position."
                else:
                    draft_state["teams"][user][position].append(player)
                    draft_state["drafted_players"].add(player)
                    advance_draft()
                    return redirect(url_for("draft", user=user))

    return render_template_string("""
    <h1>Fantasy Snake Draft</h1>
    <h2>Current Round: {{round}}</h2>
    <h3>Current Pick: {{drafter}}</h3>
    <p style="color:red;">{{message}}</p>

    {% if not complete %}
        {% if user == drafter %}
        <form method="post">
            Player Name: <input name="player"><br>
            Position:
            <select name="position">
                {% for pos in roster_template %}
                    <option value="{{pos}}">{{pos}}</option>
                {% endfor %}
            </select><br>
            <button type="submit">Draft</button>
        </form>
        {% else %}
        <p>Waiting for {{drafter}} to pick...</p>
        {% endif %}
    {% else %}
        <h2>Draft Complete</h2>
    {% endif %}

    <hr>
    <h2>Rosters</h2>
    {% for team, roster in teams.items() %}
        <h3>{{team}}</h3>
        <ul>
        {% for pos, players in roster.items() %}
            {% for p in players %}
                <li>{{pos}}: {{p}}</li>
            {% endfor %}
        {% endfor %}
        </ul>
    {% endfor %}
    """,
    user=user,
    drafter=current_drafter() if not draft_state["complete"] else "",
    round=draft_state["round"],
    teams=draft_state["teams"],
    roster_template=ROSTER_TEMPLATE,
    message=message,
    complete=draft_state["complete"]
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)


# In[ ]:




