import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL = 'https://www.aucklandmuseum.com/collections-research/collections'
HEADERS = {'User-Agent': 'Mozilla/5.0'}

resp = requests.get(URL, headers=HEADERS, timeout=30)
resp.raise_for_status()
text = resp.text
soup = BeautifulSoup(text, 'html.parser')

print('status', resp.status_code)
print('title', soup.title.string if soup.title else 'no title')
print('\n--- body class ---')
print(soup.body.attrs.get('class'))

print('\n--- script src ---')
for script in soup.find_all('script'):
    src = script.get('src')
    if src:
        print(src)

print('\n--- inline script snippets with api/search/json ---')
for script in soup.find_all('script'):
    if not script.string:
        continue
    text = script.string
    if any(token in text.lower() for token in ['api', 'search', 'collections', 'graphql', 'json', 'fetch', 'xhr']):
        print('---- snippet ----')
        print(text[:800])
        print('---- end ----')

print('\n--- href candidates ---')
for a in soup.find_all('a', href=True):
    href = a['href']
    if any(token in href.lower() for token in ['collections', 'search', 'api', 'json']):
        print(href)

print('\n--- regex candidate URLs ---')
patterns = [r'https?://[^"\s>]+', r'/[A-Za-z0-9_\-/]+api[A-Za-z0-9_\-/]*', r'/[A-Za-z0-9_\-/]+collections[A-Za-z0-9_\-/]*', r'/[A-Za-z0-9_\-/]+search[A-Za-z0-9_\-/]*']
found = set()
for patt in patterns:
    for match in re.findall(patt, text, flags=re.I):
        if len(match) > 20 and 'javascript' not in match.lower() and 'css' not in match.lower():
            found.add(match)
for item in sorted(found):
    print(item)

print('\n--- Attempt JSON extraction from HTML ---')
json_blocks = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', text, flags=re.S)
print('ld+json blocks', len(json_blocks))
for block in json_blocks[:3]:
    print(block[:800])

embedded_json = re.findall(r'\{[^\{\}]+\}', text)
print('embedded object approximations', len(embedded_json))
