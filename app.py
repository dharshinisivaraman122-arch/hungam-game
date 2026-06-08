import random
import json
import os

from flask import (
    Flask,
    render_template,
    request,
    session,
    jsonify,
    redirect,
    url_for
)

app = Flask(__name__)
app.secret_key = "hangman_pro_max_secret"

LEADERBOARD_FILE = "leaderboard.json"

WORDS = {
    "Technology": [
        {"word": "python", "hint": "Programming language"},
        {"word": "javascript", "hint": "Language of the web"},
        {"word": "database", "hint": "Stores information"}
    ],

    "Space": [
        {"word": "galaxy", "hint": "Collection of stars"},
        {"word": "planet", "hint": "Orbits a star"},
        {"word": "rocket", "hint": "Travels into space"}
    ],

    "Nature": [
        {"word": "jungle", "hint": "Dense forest"},
        {"word": "river", "hint": "Flows to the sea"},
        {"word": "mountain", "hint": "Very high landform"}
    ],

    "Sports": [
        {"word": "cricket", "hint": "Popular in India"},
        {"word": "football", "hint": "Played with goals"},
        {"word": "tennis", "hint": "Played with rackets"}
    ],

    "Food": [
        {"word": "pizza", "hint": "Italian dish"},
        {"word": "burger", "hint": "Fast food item"},
        {"word": "noodles", "hint": "Long thin food"}
    ]
}

DIFFICULTY = {
    "easy": 8,
    "medium": 6,
    "hard": 4
}


# ---------------------------
# LEADERBOARD FUNCTIONS
# ---------------------------

def load_leaderboard():

    if not os.path.exists(LEADERBOARD_FILE):
        return []

    try:
        with open(LEADERBOARD_FILE, "r") as file:
            return json.load(file)

    except:
        return []


def save_score(player, score):

    data = load_leaderboard()

    data.append({
        "player": player,
        "score": score
    })

    data = sorted(
        data,
        key=lambda x: x["score"],
        reverse=True
    )

    data = data[:10]

    with open(LEADERBOARD_FILE, "w") as file:
        json.dump(data, file, indent=4)


# ---------------------------
# NEW GAME
# ---------------------------

def create_game():

    category = random.choice(
        list(WORDS.keys())
    )

    selected = random.choice(
        WORDS[category]
    )

    session["word"] = selected["word"]
    session["hint"] = selected["hint"]
    session["category"] = category

    session["guessed"] = []

    session["wrong"] = 0

    session["score"] = 0

    session["hint_used"] = False

    session["game_over"] = False
    session["won"] = False


# ---------------------------
# ROUTES
# ---------------------------

@app.route("/")
def login_page():

    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():

    username = request.form.get(
        "username"
    )

    difficulty = request.form.get(
        "difficulty"
    )

    if not username:
        return redirect("/")

    session["player"] = username

    session["difficulty"] = difficulty

    session["games_played"] = 0
    session["games_won"] = 0

    create_game()

    return redirect(
        url_for("dashboard")
    )


@app.route("/dashboard")
def dashboard():

    if "player" not in session:
        return redirect("/")

    return render_template(
        "dashboard.html",
        player=session["player"]
    )


@app.route("/game")
def game():

    if "player" not in session:
        return redirect("/")

    return render_template("game.html")


@app.route("/state")
def state():

    word = session["word"]

    guessed = session["guessed"]

    revealed = []

    for letter in word:

        if letter in guessed:
            revealed.append(letter)

        else:
            revealed.append("_")

    return jsonify({

        "player":
        session["player"],

        "category":
        session["category"],

        "hint":
        session["hint"],

        "revealed":
        revealed,

        "wrong":
        session["wrong"],

        "max_wrong":
        DIFFICULTY[
            session["difficulty"]
        ],

        "score":
        session["score"],

        "hint_used":
        session["hint_used"],

        "game_over":
        session["game_over"],

        "won":
        session["won"],

        "word":
        word if session["game_over"] else ""
    })


@app.route(
    "/guess",
    methods=["POST"]
)
def guess():

    if session["game_over"]:
        return jsonify({
            "error":
            "Game Over"
        })

    data = request.get_json()

    letter = data.get(
        "letter",
        ""
    ).lower()

    if (
        not letter
        or len(letter) != 1
    ):
        return jsonify({
            "error":
            "Invalid"
        })

    if letter in session["guessed"]:

        return jsonify({
            "error":
            "Already guessed"
        })

    guessed = session["guessed"]

    guessed.append(letter)

    session["guessed"] = guessed

    if letter in session["word"]:

        session["score"] += 10

    else:

        session["wrong"] += 1

        session["score"] -= 2

    if all(
        l in guessed
        for l in session["word"]
    ):

        session["won"] = True

        session["game_over"] = True

        session["score"] += 50

        session["games_won"] += 1

        save_score(
            session["player"],
            session["score"]
        )

    if session["wrong"] >= DIFFICULTY[
        session["difficulty"]
    ]:

        session["game_over"] = True

    return jsonify({
        "success": True
    })


@app.route(
    "/hint",
    methods=["POST"]
)
def hint():

    if session["hint_used"]:

        return jsonify({
            "error":
            "Hint already used"
        })

    for letter in session["word"]:

        if letter not in session["guessed"]:

            guessed = session["guessed"]

            guessed.append(letter)

            session["guessed"] = guessed

            session["hint_used"] = True

            session["score"] -= 5

            break

    return jsonify({
        "success": True
    })


@app.route("/leaderboard")
def leaderboard():

    return jsonify(
        load_leaderboard()
    )


@app.route("/stats")
def stats():

    return jsonify({

        "player":
        session.get("player"),

        "games_played":
        session.get(
            "games_played",
            0
        ),

        "games_won":
        session.get(
            "games_won",
            0
        ),

        "score":
        session.get(
            "score",
            0
        )
    })


@app.route("/new_game")
def new_game():

    session["games_played"] += 1

    create_game()

    return jsonify({
        "success": True
    })


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


if __name__ == "__main__":

    app.run(
        debug=True
    )
