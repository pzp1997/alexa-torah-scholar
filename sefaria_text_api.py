from HTMLParser import HTMLParser

import requests

SEFARIA_API_ROOT = 'http://www.sefaria.org/api/'
TEXT_ENDPOINT = SEFARIA_API_ROOT + 'texts/'


def get_verse(book, chapter, verse):
    book = book.title().replace(' ', '_') if book else ''
    text_ref = '.'.join((book, chapter, verse))
    resp = requests.get(TEXT_ENDPOINT + text_ref,
                        {'context': 0, 'commentary': 0}).json()

    text = resp.get('text', '')
    if isinstance(text, (list, tuple)):
        text = str(text[0]) if len(text) else ''

    text = strip_tags(text).strip()
    text = ''.join(c for c in text if c.isalnum() or c == ' ')

    return (text.encode('utf-8'), resp.get('ref', '').encode('utf-8'))


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

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
