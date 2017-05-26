from HTMLParser import HTMLParser

import requests

SEFARIA_API_ROOT = 'http://www.sefaria.org/api/'
TEXT_ENDPOINT = SEFARIA_API_ROOT + 'texts/'


def get_text(text_ref):
    resp = requests.get(TEXT_ENDPOINT + text_ref,
                        {'context': 0, 'commentary': 0}).json()

    text = resp.get('text', '')
    if isinstance(text, (list, tuple)):
        text = ' '.join(text)
    text = _strip_tags(text).strip()

    return (text.encode('utf-8'), resp.get('ref', '').encode('utf-8'))


def get_commentary(text_ref):
    resp = requests.get(TEXT_ENDPOINT + text_ref, {'context': 0}).json()

    links = resp.get('commentary', [])
    commentaries = []
    for link in links:
        ref, text, type_ = _entrygetter('ref', 'text', 'type')(link)
        if ref and text and type_ == 'commentary':
            commentaries.append(ref)

    return (commentaries, resp.get('ref', '').encode('utf-8'))


def _entrygetter(*keys):
    if len(keys) < 1:
        raise TypeError('entrygetter expected 1 arguments, got 0')

    def entrygetter_inner(d, default=None):
        return tuple(d.get(key, default) for key in keys)
    return entrygetter_inner


def create_ref(book, chapter, start_verse=None, end_verse=None, context=0):
    book = book.title().replace(' ', '_') if book else ''

    if start_verse is None:
        return '{}.{}'.format(book, chapter)

    if context > 0:
        try:
            start_verse_int = int(start_verse)
        except ValueError:
            pass
        else:
            start_verse = str(max(start_verse_int - context, 1))
            if end_verse is None:
                end_verse = str(start_verse_int + context)
            else:
                try:
                    end_verse_int = int(end_verse)
                except ValueError:
                    pass
                else:
                    end_verse = str(end_verse_int + context)

    if end_verse is None:
        return '{}.{}.{}'.format(book, chapter, start_verse)

    return '{}.{}.{}-{}'.format(book, chapter, start_verse, end_verse)


# Strips HTML tags from a string
# Created by Stack Overflow user Eloff in his/her answer to the question
# https://stackoverflow.com/questions/753052/strip-html-from-strings-in-python

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def _strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
