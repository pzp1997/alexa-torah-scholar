import requests

SEFARIA_API_ROOT = 'http://www.sefaria.org/api/'
TEXT_ENDPOINT = SEFARIA_API_ROOT + 'texts/'


def get_verse(book, chapter, verse):
    text_ref = '.'.join((book, chapter, verse))
    resp = requests.get(TEXT_ENDPOINT + text_ref,
                        {'context': 0, 'commentary': 0}).json()
    return {
        'text': resp.get('text'),
        'ref': resp.get('ref')
    }
