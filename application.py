import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///users.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/", methods=["GET", "POST"])
@login_required
def profile():
    """User Profile"""
    user_id = session["user_id"]

    if request.method == "POST":
        new_language = request.form.get("new_language")
        overview_languages = db.execute("SELECT * FROM languages WHERE user_id = :user_id", user_id = user_id)
        if new_language in overview_languages:
            return apology("You are already working on it!", 403)

        else:
            add_new_language = db.execute("INSERT INTO languages (language, user_id) VALUES (:language, :user_id)", language = new_language, user_id = user_id)
            return redirect("/")

    else:
        overview_languages = db.execute("SELECT * FROM languages WHERE user_id = :user_id", user_id = user_id)
        if not overview_languages:
            return render_template("profile.html", message = "No languages at the moment!")
        else:
            return render_template("profile.html", overview_languages = overview_languages)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"]) #DONE
def register():
    """Register user"""

    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            return apology("Invalid Username, try again.")

        password = request.form.get("password")
        if not password:
            return apology("Invalid Password, try again.")

        conf_pw = request.form.get("conf_pw")
        if conf_pw != password:
            return apology("The Password doesn't match, try again.")

        db.execute("SELECT username FROM users WHERE username = :username", username = username)
        if len(username) == 1:
            return apology("Username not available, try again")

        else:
            new_user = db.execute("INSERT INTO users (username, hash) VALUES (:username, :password)", username = username, password = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8))

            if new_user:
                session["user_id"] = new_user
                return redirect("/")

    else:
        return render_template("register.html")


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """ADD CARD"""
    word = request.form.get("word")
    definition = request.form.get("definition")
    lang_in_db = request.form.get("lang_in_db")


    if request.method == "POST":
        user_id = session["user_id"]
        overview_languages = db.execute("SELECT * FROM languages WHERE user_id = :user_id", user_id = user_id)
        if lang_in_db in overview_languages:
            return apology("You are already working on it!", 403)
        else:
            add_card = db.execute("INSERT INTO flashcards (user_id, language, word, definition) VALUES (:user_id, :language, :word, :definition)", user_id = user_id, language = lang_in_db, word = word, definition = definition)
            add_flashcard_to_db = db.execute("UPDATE languages SET flashcards = flashcards + 1 WHERE user_id = :user_id AND language = :language", user_id = user_id, language = lang_in_db)
            return redirect("/add")

    else:
        user_id = session["user_id"]
        overview_languages = db.execute("SELECT * FROM languages WHERE user_id = :user_id", user_id = user_id)
        if not overview_languages:
            return apology("Choose a language to learn first!")
        else:
            db_user = db.execute("SELECT * FROM flashcards WHERE user_id = :user_id", user_id = user_id)
            if not db_user:
                return render_template("add.html", overview_languages = overview_languages, message="No flashards yet!")
            else:
                return render_template("add.html", overview_languages = overview_languages, db_user = db_user)


@app.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    """QUIZ"""
    user_id = session["user_id"]
    overview_languages = db.execute("SELECT * FROM languages WHERE user_id = :user_id", user_id = user_id)

    if request.method == "POST":
        quiz_language = request.form.get("quiz_language")
        db_user = db.execute("SELECT * FROM flashcards WHERE user_id = :user_id AND language = :quiz_language", user_id = user_id, quiz_language = quiz_language)
        session['quiz_language'] = quiz_language
        return redirect("/quiztab")

    else:
        count_quiz = db.execute("SELECT COUNT(*) as count FROM quizzes WHERE user_id = :user_id", user_id = user_id)
        all_quizzes = db.execute("SELECT * FROM quizzes WHERE user_id = :user_id", user_id = user_id)

        if not overview_languages:
            return render_template("quiz.html", message="No languages at the moment!")
        elif not count_quiz:
            return render_template("quiz.html", message="No quizzes taken yet!", overview_languages = overview_languages, count_quiz = count_quiz)
        else:
            return render_template("quiz.html", overview_languages = overview_languages, count_quiz = count_quiz[0]["count"], all_quizzes = all_quizzes)


@app.route("/quiztab", methods=["GET", "POST"])
@login_required
def quiztab():
    """QUIZTAB"""
    quiz_language = session.get('quiz_language', None)
    user_id = session["user_id"]
    overview_languages = db.execute("SELECT * FROM languages WHERE user_id = :user_id", user_id = user_id)
    db_user = db.execute("SELECT * FROM flashcards WHERE user_id = :user_id AND language = :quiz_language", user_id = user_id, quiz_language = quiz_language)
    cards = db.execute("SELECT word, definition FROM flashcards WHERE user_id = :user_id AND language = :quiz_language", user_id = user_id, quiz_language = quiz_language)
    n_cards = db.execute("SELECT COUNT(*) as count FROM flashcards WHERE user_id = :user_id AND language = :quiz_language", user_id = user_id, quiz_language = quiz_language)[0]["count"]
    id_flashcards = db.execute("SELECT id_flashcard FROM flashcards WHERE user_id = :user_id AND language = :quiz_language", user_id = user_id, quiz_language = quiz_language)
    quiz = cards = db.execute("SELECT id_flashcard, word, definition FROM flashcards WHERE user_id = :user_id AND language = :quiz_language", user_id = user_id, quiz_language = quiz_language)


    if request.method == "POST":
        data = request.form.to_dict()

        result = 0

        for x in range(len(data)):

            check1 = int(list(data.keys())[x])
            check2 = quiz[x]['id_flashcard']
            check3 = list(data.values())[x]
            check4 = quiz[x]['word']

            if check1 == check2 and check3 == check4:
                result += 1

        add_quiz = db.execute("UPDATE languages SET quiz = quiz + 1 WHERE user_id = :user_id AND language = :quiz_language", user_id = user_id, quiz_language = quiz_language)
        avg = ((result / n_cards) * 100)
        update_quizzes = db.execute("INSERT INTO quizzes (user_id, language, n_flashcards, correct_answers, avg_quiz) VALUES (:user_id, :language, :n_flashcards, :correct_answers, :avg)", user_id = user_id, language = quiz_language, n_flashcards = n_cards, correct_answers = result, avg = avg)
        sum_avg_quizzes = db.execute("SELECT SUM(avg_quiz) as sum FROM quizzes WHERE user_id = :user_id AND language = :quiz_language", user_id = user_id, quiz_language = quiz_language)[0]["sum"]
        quiz_n = db.execute("SELECT COUNT(*) as count FROM quizzes WHERE user_id = :user_id AND language = :quiz_language", user_id = user_id, quiz_language = quiz_language)[0]["count"]
        tot_avg_quizzes = sum_avg_quizzes / quiz_n
        update_avg_quiz = db.execute("UPDATE languages SET average = :average WHERE user_id = :user_id AND language = :quiz_language", average = tot_avg_quizzes, user_id = user_id, quiz_language = quiz_language)

        return redirect("/quiz")

    else:
        if not cards:
            return render_template("quiztab.html", message="No cards yet!")
        else:
            return render_template("quiztab.html", db_user = db_user, quiz = quiz)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
