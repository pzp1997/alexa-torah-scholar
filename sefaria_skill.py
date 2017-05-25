from flask import Flask, render_template
from flask_ask import Ask, convert_errors, question, session, statement

from sefaria_api import create_ref, get_commentary, get_text

app = Flask(__name__)
ask = Ask(app, '/')

@ask.intent('VerseIntent', default={'chapter': '1', 'verse': '1'})
def handle_verse_intent(book, chapter, verse):
    app.logger.info('VerseIntent for %s %s:%s', book, chapter, verse)
    text, ref = sefaria.get_text(book, chapter, verse, verse)
    app.logger.debug(text)
    return _build_text_response(text, ref)


@ask.intent('ChapterIntent', default={'chapter': '1'})
def handle_chapter_intent(book, chapter):
    app.logger.info('ChapterIntent for %s %s', book, chapter)
    text, ref = sefaria.get_text(book, chapter)
    app.logger.debug(text)
    return _build_text_response(text, ref)


@ask.intent('VerseRangeIntent', default={'chapter': '1', 'start_verse': '1', 'end_verse': '1'})
def handle_verse_range_intent(book, chapter, start_verse, end_verse):
    app.logger.info('VerseRangeIntent for %s %s:%s-%s', book, chapter, start_verse, end_verse)
    text, ref = sefaria.get_text(book, chapter, start_verse, end_verse)
    app.logger.debug(text)
    return _build_text_response(text, ref)


@ask.launch
def launched():
    text = render_template('launch')
    return question(text)


@ask.session_ended
def session_ended():
    return '', 200


def _build_text_response(text, ref):
    if text:
        card_text = (text[:137] + '...' if len(text) > 140 else text)
        speech_text = '{}{}{}'.format(ref, '. ' if ref else '', text)
        card_title = 'Sefaria{}{}'.format(' - ' if ref else '', ref)
        return statement(speech_text).simple_card(card_title, card_text)
    else:
        ref = ref or 'the text'
        err_msg = render_template('error', ref=ref)
        return statement(err_msg).simple_card('Error', err_msg)


if __name__ == '__main__':
    app.run(debug=True)
