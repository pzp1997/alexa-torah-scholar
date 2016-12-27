from flask import Flask
from flask import render_template

from flask_ask import Ask
from flask_ask import statement
from flask_ask import question

import sefaria_text_api as sefaria

app = Flask(__name__)
ask = Ask(app, '/')


@ask.intent('VerseIntent')
def verse(book, chapter, verse):
    text = sefaria.get_verse(book, chapter, verse)
    return statement(text).simple_card('Hello', text)


@ask.launch
def launched():
    text = render_template('launch')
    return question(text)


@ask.session_ended
def session_ended():
    return "", 200

if __name__ == '__main__':
    app.run(debug=True)
