import requests
from bs4 import BeautifulSoup

url = 'https://www.aucklandmuseum.com/collections-research/collections'
headers = {'User-Agent': 'Mozilla/5.0'}
resp = requests.get(url, headers=headers, timeout=20)
text = resp.text
soup = BeautifulSoup(text, 'html.parser')
print('status', resp.status_code)
print('title', soup.title.string if soup.title else 'no title')

print('\n--- SCRIPTS ---')
for script in soup.find_all('script'):
    src = script.get('src')
    if src:
        print('SRC', src)

print('\n--- ANCHORS ---')
for a in soup.find_all('a', href=True):
    href = a['href']
    if 'collections' in href.lower() or 'search' in href.lower() or 'api' in href.lower() or 'json' in href.lower():
        print('HREF', href)

print('\n--- INLINE SCRIPT KEYS ---')
keys = ['fetch(', 'axios', 'XMLHttpRequest', 'dataLayer', 'window.dataLayer', 'api', 'graphql', 'search', 'json']
for script in soup.find_all('script'):
    if script.string:
        text = script.string
        for key in keys:
            if key in text:
                print('INLINE KEY', key)
                print(text[:400])
                raise SystemExit
