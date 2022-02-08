# iexcloud
# export API_KEY=pk_34f849efbf6644aba48eefa67beb7b67

# quiztab block main
{% block main %}
<header class="masthead">
    <div class="container h-100">
        <div class="row h-100 align-items-center justify-content-center text-center">
            <div class="col-lg-10 align-self-end mt-5 mb-3">
            {% if message is defined %}
                <table class="table table-sm table-bordered">
                    <thead>
                        <tr>
                          <th scope="col">{{ message }}</th>
                        </tr>
                    </thead>
                </table>
            {% else %}
            <h2 class="mb-5">ready, set.. go!</h2>
            <div class="row">
                <form action="/quiztab" method="post">
                {% for card in db_user %}
                <div class="form-group row roundform">
                    <label for="staticEmail" class="col-sm-5 col-form-label" name="def_quiz[{{ card['id_flashcard'] }}]">{{ card["definition"] }}</label>
                    <h4>{{ card["id_flashcard"] }}</h4>
                    <h4>{{ id_flashcards }}</h4>
                    <div class="col-sm-10">
                        <input autocomplete="off" class="form-control roundform" type="text" name="answer[{{ card['id_flashcard'] }}]" placeholder="Write here the correct translation!">
                    </div>
                </div>
                {% endfor %}
                <hr class="divider my-4 mt-5 mb-3" />
                <button class="roundbutton mt-5" type="submit">Give me the results!</button>
                </form>
            {% endif %}
            </div>
        </div>
    </div>
</section>
{% endblock %}


# application.py quiztab
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

    answer = []
    def_quiz = []

    if request.method == "POST":
        answer.append(request.form.get("answer[{{ card['id_flashcard'] }}]"))
        def_quiz.append(request.form.get("def_quiz[{{ card['id_flashcard'] }}]"))

        results = 0

        for x in answer:
            for y in def_quiz:
                correct_word = db.execute("SELECT word FROM flashcards WHERE user_id = :user_id AND language = :quiz_language AND definition = :definition", user_id = user_id, quiz_language = quiz_language, definition = def_quiz)
                if correct_word == answer:
                    results = results + 1
                else:
                    results = results

        add_quiz = db.execute("UPDATE languages SET quiz = quiz + 1 WHERE user_id = :user_id AND language = :quiz_language", user_id = user_id, quiz_language = quiz_language)
        avg = ((results / n_cards) * 100)
        update_quizzes = db.execute("INSERT INTO quizzes (user_id, language, n_flashcards, correct_answers, avg_quiz) VALUES (:user_id, :language, :n_flashcards, :correct_answers, :avg)", user_id = user_id, language = quiz_language, n_flashcards = n_cards, correct_answers = results, avg = avg)

        answer = []
        def_quiz = []
        return redirect("/quiz")

    else:
        if not cards:
            return render_template("quiztab.html", message="No cards yet!")
        else:
            return render_template("quiztab.html", db_user = db_user, id_flashcards = id_flashcards)