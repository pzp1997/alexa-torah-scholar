from flask import Flask, render_template
from flask_ask import Ask, convert_errors, question, session, statement

from sefaria_api import create_ref, get_commentary, get_text

app = Flask(__name__)
ask = Ask(app, '/')


@ask.intent('ChapterIntent')
def handle_chapter_intent(book, chapter):
    session.attributes['last_intent'] = 'ChapterIntent'
    app.logger.info('ChapterIntent: %s %s', book, chapter)
    return handle_text_request(book, chapter, None, None)


@ask.intent('VerseIntent')
def handle_verse_intent(book, chapter, verse):
    session.attributes['last_intent'] = 'VerseIntent'
    app.logger.info('VerseIntent: %s %s %s', book, chapter, verse)
    return handle_text_request(book, chapter, verse, None)


@ask.intent('VerseRangeIntent')
def handle_verse_range_intent(book, chapter, start_verse, end_verse):
    session.attributes['last_intent'] = 'VerseRangeIntent'
    app.logger.info('VerseRangeIntent: %s %s %s %s',
                    book, chapter, start_verse, end_verse)
    return handle_text_request(book, chapter, start_verse, end_verse)


def handle_text_request(book, chapter, start_verse, end_verse):
    ref = create_ref(book, chapter, start_verse, end_verse)
    text, ref = get_text(ref)
    app.logger.debug(text)

    session.attributes['last_ref'] = ref
    return _build_text_response(text, ref)


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
        err_msg = render_template('error', ref=(ref or 'the text'))
        return statement(err_msg).simple_card('Error', err_msg)


if __name__ == '__main__':
    app.run(debug=True)
