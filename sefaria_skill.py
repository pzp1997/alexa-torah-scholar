from flask import Flask
from flask import render_template

from flask_ask import Ask
from flask_ask import statement
from flask_ask import question

import sefaria_text_api as sefaria

app = Flask(__name__)
ask = Ask(app, '/')


@ask.intent('VerseIntent', default={'chapter': '1', 'verse': '1'})
def verse_intent(book, chapter, verse):
    api_resp = sefaria.get_verse(book, chapter, verse)
    text, ref = api_resp['text'], api_resp['ref']

    if text:
        return statement(text).simple_card(ref, text)
    else:
        ref = ref or 'text'
        err_msg = render_template('error', ref=ref)
        return statement(err_msg).simple_card('Error', err_msg)


@ask.launch
def launched():
    text = render_template('launch')
    return question(text)


@ask.session_ended
def session_ended():
    return "", 200

if __name__ == '__main__':
    app.run(debug=True)
