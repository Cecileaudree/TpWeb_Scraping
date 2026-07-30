import requests
from bs4 import BeautifulSoup

URL = 'https://www.aucklandmuseum.com/discover/collections/search'
HEADERS = {'User-Agent': 'Mozilla/5.0'}
resp = requests.get(URL, headers=HEADERS, timeout=30)
resp.raise_for_status()
text = resp.text
soup = BeautifulSoup(text, 'html.parser')

print('status', resp.status_code)
print('title', soup.title.string if soup.title else 'no title')
print('len html', len(text))

selectors = ['div', 'section', 'article', 'li']
keywords = ['result', 'item', 'search', 'card', 'grid', 'collection', 'object', 'list', 'hit', 'preview']
found = []
for tag in selectors:
    for el in soup.find_all(tag):
        cls = el.get('class')
        if not cls:
            continue
        cls_s = ' '.join(cls).lower()
        if any(keyword in cls_s for keyword in keywords):
            text = el.get_text(' ', strip=True)
            if len(text) < 20:
                continue
            found.append((tag, cls_s, text[:160]))
            if len(found) >= 40:
                break
    if len(found) >= 40:
        break

print('found', len(found))
for tag, cls, text in found[:40]:
    print(tag, cls, repr(text))

print('\nhidden inputs:')
for inp in soup.select('form input[type=hidden]'):
    print(inp.get('name'), inp.get('value')[:40] if inp.get('value') else None)
