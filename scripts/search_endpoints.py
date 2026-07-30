import requests
import re
from bs4 import BeautifulSoup

BASE = 'https://www.aucklandmuseum.com'
URL = BASE + '/discover/collections/search'
headers = {'User-Agent': 'Mozilla/5.0'}
resp = requests.get(URL, headers=headers, timeout=30)
resp.raise_for_status()
text = resp.text
soup = BeautifulSoup(text, 'html.parser')

print('status', resp.status_code)
print('title', soup.title.string if soup.title else 'no title')

for pattern in [r'WebService\.asmx', r'webservice\.asmx', r'\.asmx', r'\.ashx', r'api/', r'api\\?', r'fetch\(', r'ajax\(', r'__doPostBack\(', r'__VIEWSTATE', r'__EVENTVALIDATION', r'json']:
    matches = re.findall(pattern, text, flags=re.I)
    if matches:
        print('\nPATTERN', pattern, 'count', len(matches))
        for match in matches[:20]:
            print(' ', match)

print('\n--- unique URLs in HTML ---')
urls = set(re.findall(r'https?://[^"\s<>]+', text))
ish = set(re.findall(r'/(?:[A-Za-z0-9_\-./?=&%]+)', text))
for u in sorted(urls)[:50]:
    print('URL', u)
print('--- partial urls ---')
for u in sorted(ish)[:50]:
    if any(k in u.lower() for k in ['asmx', 'ashx', 'api', 'search', 'json', 'collections', 'discover', 'load']):
        print('PART', u)
