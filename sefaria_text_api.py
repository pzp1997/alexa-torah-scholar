from HTMLParser import HTMLParser

import requests

SEFARIA_API_ROOT = 'http://www.sefaria.org/api/'
TEXT_ENDPOINT = SEFARIA_API_ROOT + 'texts/'


def get_text(book, chapter, start_verse=None, end_verse=None):
    text_ref = _create_ref(book, chapter, start_verse, end_verse)

    resp = requests.get(TEXT_ENDPOINT + text_ref,
                        {'context': 0, 'commentary': 0}).json()

    text = resp.get('text', '')

    if isinstance(text, (list, tuple)):
        if (start_verse is None) ^ (end_verse is None):
            text = text[0] if len(text) else ''
        else:
            text = ' '.join(text)

    text = _strip_tags(text).strip()
    # text = ''.join(c for c in text if c.isalnum() or c == ' ')

    return (text.encode('utf-8'), resp.get('ref', '').encode('utf-8'))


def _create_ref(book, chapter, start_verse, end_verse):
    book = book.title().replace(' ', '_') if book else ''
    if start_verse is None:
        return '{}.{}'.format(book, chapter)
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
