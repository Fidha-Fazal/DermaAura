import requests
BASE='http://localhost:5000'
r = requests.get(BASE + '/shop')
html = r.text
fn = 'abcb18e23cff4771b2ae5e2dec762509.png'
if fn in html:
    i = html.find(fn)
    start = html.rfind('<img', 0, i)
    end = html.find('>', i)
    print('Found image tag snippet:')
    print(html[start:end+1])
else:
    print('Filename not present in /shop HTML')
    # show snippet around where product name appears
    if 'TestPNG' in html:
        i = html.find('TestPNG')
        print(html[i-200:i+200])
