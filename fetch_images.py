"""Fetch real product images using an image API and update database.

Supports Unsplash (preferred) or Pexels. Set one of the following
environment variables with your API key before running:

  export UNSPLASH_ACCESS_KEY=<your key>
  export PEXELS_API_KEY=<your key>

Usage:
    python fetch_images.py

The script will query the API for each product name, download the first
result, save it under ``app/static/images/`` and update ``product.image``
with the new path.

If no key is configured or no photo found for a product, the existing image
remains intact.
"""

import os
import re
import time
import requests
from app import create_app, db
from models import Product

IMAGE_DIR = os.path.join(os.getcwd(), "app", "static", "images")
os.makedirs(IMAGE_DIR, exist_ok=True)

UNSPLASH_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")

if not UNSPLASH_KEY and not PEXELS_KEY:
    print("ERROR: Set UNSPLASH_ACCESS_KEY or PEXELS_API_KEY environment variable.")
    print("See README for instructions.")
    exit(1)

USE_UNSPLASH = bool(UNSPLASH_KEY)
USE_PEXELS = bool(PEXELS_KEY) and not USE_UNSPLASH  # prioritize Unsplash

HEADERS = {}
API_RATE_DELAY = 1.0

if USE_UNSPLASH:
    HEADERS = {"Authorization": f"Client-ID {UNSPLASH_KEY}"}
elif USE_PEXELS:
    HEADERS = {"Authorization": PEXELS_KEY}


def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:60]


def search_unsplash(query: str):
    url = "https://api.unsplash.com/search/photos"
    resp = requests.get(url, headers=HEADERS, params={"query": query, "per_page": 1})
    if resp.status_code == 200:
        data = resp.json()
        results = data.get("results") or []
        if results:
            return results[0]["urls"]["regular"]
    return None


def search_pexels(query: str):
    url = "https://api.pexels.com/v1/search"
    resp = requests.get(url, headers=HEADERS, params={"query": query, "per_page": 1})
    if resp.status_code == 200:
        data = resp.json()
        photos = data.get("photos") or []
        if photos:
            return photos[0]["src"]["medium"]
    return None


def download_image(url: str, dest: str) -> bool:
    try:
        r = requests.get(url, timeout=30)
        if r.status_code == 200 and "image" in r.headers.get("Content-Type", ""):
            with open(dest, "wb") as f:
                f.write(r.content)
            return True
    except Exception:
        pass
    return False


def main():
    app = create_app()
    with app.app_context():
        products = Product.query.all()
        for idx, p in enumerate(products, start=1):
            query = p.name or "product"
            q = re.sub(r"[^a-zA-Z0-9 ]", "", query)
            q = " ".join(q.split())

            print(f"[{idx}/{len(products)}] {p.name}")

            if USE_UNSPLASH:
                img_url = search_unsplash(q)
            else:
                img_url = search_pexels(q)

            if not img_url:
                print("  no image found")
                time.sleep(API_RATE_DELAY)
                continue

            fname = slugify(p.name) + f"-{p.id}.jpg"
            dest = os.path.join(IMAGE_DIR, fname)
            success = download_image(img_url, dest)
            if success:
                p.image = f"/static/images/{fname}"
                db.session.add(p)
                print("  downloaded and updated")
            else:
                print("  download failed")

            time.sleep(API_RATE_DELAY)
        db.session.commit()

if __name__ == '__main__':
    main()
