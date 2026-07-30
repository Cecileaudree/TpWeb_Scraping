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
print('\n--- form ---')
for form in soup.find_all('form'):
    print('FORM action=', form.get('action'), 'method=', form.get('method'))
    for inp in form.find_all(['input','select','textarea']):
        print(' ', inp.name, inp.get('type'), inp.get('value'))

print('\n--- script src ---')
for script in soup.find_all('script'):
    if script.get('src'):
        print('SRC', script.get('src'))

print('\n--- inline snippet search ---')
for script in soup.find_all('script'):
    if script.string and ('fetch(' in script.string or 'ajax' in script.string or 'json' in script.string or 'webservice' in script.string or 'xhr' in script.string):
        print('--- script snippet ---')
        print(script.string[:1200])
        print('--- end ---')
