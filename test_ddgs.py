from duckduckgo_search import DDGS
import time

def test_fetch():
    product = "Cetaphil Gentle Skin Cleanser bottle"
    with DDGS() as ddgs:
        results = list(ddgs.images(product, max_results=1))
        if results:
            print(f"Found: {results[0]['image']}")
        else:
            print("Not found")

if __name__ == '__main__':
    test_fetch()
