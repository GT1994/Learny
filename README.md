## CS50's Final Project by Giulia Tempofosco (github @GT1994)

For my CS50's final project I wanted to create a space which could improve the way people learn languages, with a sustainable twist.
Flashcards can be a very effective aid to help remembering words, but there is always a big waste of paper.
To solve the problem, I created

**Learny**
Learny is the prototype of a platform for users to create fully customizable flashcards and test their abilities with quizzes.
All progresses are tracked in order to give the users a record of improvement in a certain language.

**Environment**
Flask, Python, HTML, CSS, SQL

**Link to video**
https://youtu.be/lh5r6wzvE8s

## How does it work?
**Register / Login**
Users need to register on the website in order to be part of Learny's database and start their learning process.
Each user is going to be added to a database (users.db) with:
- username
- password
- ID

**Homepage - Profile**
Once logged in, on the homepage it is possible to get an overview for each language learned of:
- number of flashcards created
- number quizzes taken
- average of quizzes' taken

It is also possible to add new languages to learn from the drop-down menu.

**Add Flashcard**
On this page the user can add new flashcards, to enrich their personal flashcard database.
Users can choose the preferred language, word/expression to be learned and definition.
Because some languages require the use of capital letters, case sensitivity is relevant.
The information is then stored in a database (flashcards.db) in this way:
- id flashcard
- language of the flashcard
- word
- definition
- user id

**Quiz**
This page allows the user to either just have an overview of all the quiz taken or to start a new one.
The overview is through a table connected to the database quizzes.db, which shows:
- language of the quiz
- number of flashcards used in that specific quiz
- correct answers of that specific quiz
- average of that specific quiz
- date

To start a new quiz, the user has to first select a language from the dropdown menu, which shows all the languages from the profile section.
The user will be then redirected to /quiztab to take the actual quiz.

**Quiztab**
In this page the user will see all the cards on his database for the specific language he/she choose in /quiz, showing just the definition.
The user will have to fill each input field with the correct word/expression and, once finished, press the button and be redirected to /quiz, where the result of the quiz just taken will be shown on the tab.
This will also update the average on the homepage.

**Logout**
Once the learning session is finished, the user will just have to press "logout" from the menu and he/she will be redirected to /login.

