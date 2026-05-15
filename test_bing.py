import requests
import re
import random

def fetch_bing_image(query):
    url = f"https://www.bing.com/images/search?q={requests.utils.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    matches = re.findall(r'murl&quot;:&quot;(.*?)&quot;', response.text)
    if matches:
        return matches[0]
    return None

if __name__ == "__main__":
    print(fetch_bing_image("Cetaphil Gentle Skin Cleanser 250ml white background"))
