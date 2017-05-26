from flask import Flask, render_template
from flask_ask import Ask, convert_errors, question, session, statement

from sefaria_api import create_ref, get_commentary, get_text

app = Flask(__name__)
ask = Ask(app, '/')


@ask.intent('ChapterIntent')
def handle_chapter_intent(book, chapter):
    session.attributes['last_intent'] = 'ChapterIntent'
    app.logger.info('ChapterIntent: %s %s', book, chapter)
    text, ref = handle_text_request(book, chapter, None, None)
    return _build_text_response(text, ref)


@ask.intent('VerseIntent')
def handle_verse_intent(book, chapter, verse):
    session.attributes['last_intent'] = 'VerseIntent'
    app.logger.info('VerseIntent: %s %s %s', book, chapter, verse)
    text, ref = handle_text_request(book, chapter, verse, None)
    return _build_verse_response(text, ref)


@ask.intent('VerseRangeIntent')
def handle_verse_range_intent(book, chapter, start_verse, end_verse):
    session.attributes['last_intent'] = 'VerseRangeIntent'
    app.logger.info('VerseRangeIntent: %s %s %s %s',
                    book, chapter, start_verse, end_verse)
    text, ref = handle_text_request(book, chapter, start_verse, end_verse)
    return _build_verse_response(text, ref)


def handle_text_request(book, chapter, start_verse, end_verse):
    text_request = (book, chapter, start_verse, end_verse)
    session.attributes['last_ref'] = text_request
    ref = create_ref(*text_request)
    text, ref = get_text(ref)
    app.logger.debug(text)
    return text, ref


@ask.intent('CommentaryIntent', default={'chapter': '1', 'verse': '1'})
def handle_commentary_intent(book, chapter, verse):
    session.attributes['last_intent'] = 'CommentaryIntent'
    app.logger.info('CommentaryIntent: %s %s %s', book, chapter, verse)
    ref = create_ref(book, chapter, verse)
    return _commentary_helper(ref)


@ask.intent('CommentarySelectionIntent', convert={'commentary_number': int})
def handle_commentary_selection_intent(commentary_number):
    session.attributes['last_intent'] = 'CommentarySelectionIntent'
    app.logger.info('CommentarySelectionIntent: %s', commentary_number)

    commentaries = session.attributes.get('commentaries')
    if not commentaries:
        return _build_could_not_find_response('any commentaries')

    if ('commentary_number' in convert_errors or
            commentary_number < 1 or commentary_number > len(commentaries)):
        speech_text = render_template('commentary_reprompt',
                                      number=len(commentaries))
        return question(speech_text)

    text, ref = get_text(commentaries[commentary_number - 1])
    app.logger.debug(text)

    return _build_text_response(text, ref)


@ask.launch
def launched():
    text = render_template('launch')
    return question(text)


@ask.session_ended
def session_ended():
    return '', 200


def _commentary_helper(text_ref):
    commentary_refs, ref = get_commentary(text_ref)
    app.logger.debug(commentary_refs)
    session.attributes['commentaries'] = commentary_refs
    return _build_commentary_response(commentary_refs, ref)


def _build_text_response(text, ref):
    if text:
        card_text = (text[:137] + '...' if len(text) > 140 else text)
        speech_text = '{}{}{}'.format(ref, '. ' if ref else '', text)
        card_title = 'Sefaria{}{}'.format(' - ' if ref else '', ref)
        return statement(speech_text).simple_card(card_title, card_text)
    else:
        return _build_could_not_find_response(ref or 'the text')


def _build_commentary_response(commentaries, ref):
    if commentaries:
        num_commentaries = len(commentaries)

        if num_commentaries == 1:
            text, ref = get_text(commentaries[0])
            app.logger.debug(text)
            return _build_text_response(text, ref)

        speech_text = render_template(
            'commentary', number=num_commentaries, ref=ref,
            titles=', '.join('{}. {}'.format(i, ref) for i, ref
                             in enumerate(commentaries, start=1)))

        reprompt_text = render_template('commentary_reprompt',
                                        number=num_commentaries)

        return question(speech_text).reprompt(reprompt_text)
    else:
        if ref:
            err_msg = render_template('commentary_none', ref=ref)
            return statement(err_msg)
        else:
            return _build_could_not_find_response('the text')


def _build_could_not_find_response(resource):
    err_msg = render_template('error', ref=resource)
    return statement(err_msg)


if __name__ == '__main__':
    app.run(debug=True)
