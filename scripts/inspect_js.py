import requests
from bs4 import BeautifulSoup

BASE = 'https://www.aucklandmuseum.com'
URL = f'{BASE}/discover/collections/search'
HEADERS = {'User-Agent': 'Mozilla/5.0'}
resp = requests.get(URL, headers=HEADERS, timeout=30)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, 'html.parser')

scripts = []
for script in soup.find_all('script'):
    src = script.get('src')
    if not src:
        continue
    if src.startswith('http'):
        scripts.append(src)
    else:
        scripts.append(BASE + src if src.startswith('/') else BASE + '/' + src)

print('found', len(scripts), 'scripts')
for i, src in enumerate(scripts[:20], 1):
    print(i, src)

keywords = ['api', 'search', 'collections', 'json', 'asmx', 'webservice', 'fetch', 'ajax', 'GraphQL', 'xhr']
for src in scripts:
    if 'jquery' in src or 'modernizr' in src or 'lazysizes' in src or 'google.com' in src:
        continue
    try:
        r = requests.get(src, headers=HEADERS, timeout=30)
        text = r.text
    except Exception as exc:
        print('ERROR fetching', src, exc)
        continue
    hits = [k for k in keywords if k.lower() in text.lower()]
    if hits:
        print('\nSCRIPT', src)
        print('status', r.status_code, 'size', len(text), 'hits', hits)
        for k in hits:
            for idx, line in enumerate(text.splitlines(), 1):
                if k.lower() in line.lower():
                    print(idx, line.strip()[:320])
                    if idx > 40:
                        break
            print('---')
