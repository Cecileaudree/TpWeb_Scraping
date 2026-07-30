import requests
from bs4 import BeautifulSoup

BASE = 'https://www.aucklandmuseum.com'
SEARCH_URL = BASE + '/discover/collections/search'
HEADERS = {'User-Agent': 'Mozilla/5.0'}

session = requests.Session()
resp = session.get(SEARCH_URL, headers=HEADERS, timeout=30)
resp.raise_for_status()

soup = BeautifulSoup(resp.text, 'html.parser')
form = soup.find('form')
if not form:
    raise SystemExit('No form found')

payload = {}
for inp in form.find_all(['input', 'textarea', 'select']):
    name = inp.get('name')
    if not name:
        continue
    value = inp.get('value', '')
    if inp.get('type') == 'checkbox':
        # default unchecked unless there is a checked attr
        if inp.has_attr('checked'):
            payload[name] = value
        continue
    payload[name] = value

# Set a sample keyword to trigger results
payload['ctl00$ctl00$cphMain$cphChildColumnMiddle$ctl00$txtKeyword'] = 'maori'
payload['ctl00$ctl00$ctl03$ucTopNav$txtSearch'] = ''

print('Posting', len(payload), 'fields')
resp2 = session.post(SEARCH_URL, data=payload, headers=HEADERS, timeout=30)
print('status', resp2.status_code)
print('len', len(resp2.text))

soup2 = BeautifulSoup(resp2.text, 'html.parser')
print('title', soup2.title.string if soup2.title else 'no title')

results = []
for el in soup2.select('div, li, article'):
    cls = el.get('class')
    if not cls:
        continue
    cls_s = ' '.join(cls).lower()
    if 'search' in cls_s or 'result' in cls_s or 'object' in cls_s or 'preview' in cls_s or 'item' in cls_s:
        text = el.get_text(' ', strip=True)
        if len(text) > 100:
            results.append((cls_s, text[:300]))
print('results candidate count', len(results))
for i, (cls, txt) in enumerate(results[:30], 1):
    print(i, cls, txt)

# Print first 100 lines containing 'href' or 'article' or 'title'
for i, line in enumerate(resp2.text.splitlines(), 1):
    if 'href=' in line or 'article' in line or 'preview' in line or 'class=' in line and 'object' in line:
        print(i, line.strip()[:300])
        if i > 120:
            break
