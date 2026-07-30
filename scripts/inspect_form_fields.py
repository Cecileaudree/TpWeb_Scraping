import requests
from bs4 import BeautifulSoup

URL = 'https://www.aucklandmuseum.com/discover/collections/search'
HEADERS = {'User-Agent': 'Mozilla/5.0'}
resp = requests.get(URL, headers=HEADERS, timeout=30)
resp.raise_for_status()

soup = BeautifulSoup(resp.text, 'html.parser')
form = soup.find('form')
print('form action', form.get('action'), 'method', form.get('method'))
for inp in form.find_all(['input', 'select', 'textarea']):
    print('TAG', inp.name, 'TYPE', inp.get('type'), 'NAME', inp.get('name'), 'VALUE', (inp.get('value') or '')[:80], 'CLASS', inp.get('class'))
