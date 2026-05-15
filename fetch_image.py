import requests
url='http://localhost:5000/static/images/abcb18e23cff4771b2ae5e2dec762509.png'
r=requests.get(url)
print('status', r.status_code)
print('len', len(r.content))
print('content-type', r.headers.get('content-type'))
with open('fetched_image.png','wb') as f:
    f.write(r.content)
print('wrote fetched_image.png')
