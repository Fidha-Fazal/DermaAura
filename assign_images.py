"""Utility to update product.image paths based on files in static/images.

By default it attempts to match files by product id or name slug. You can
also supply an explicit CSV mapping of product_id to filename if you need
precise control.

Usage:
    # automatic matching by slug/id
    python assign_images.py

    # specify a directory containing images
    python assign_images.py --dir path/to/images

    # provide CSV with lines "<product_id>,<filename>"
    python assign_images.py --map mapping.csv

The script will not move any files; it only updates the database records to
point at the chosen filenames (prefixed with /static/images/).
"""

import os
import re
import csv
import argparse
from app import create_app, db
from models import Product

DEFAULT_DIR = os.path.join("app", "static", "images")


def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def load_mapping(path: str) -> dict:
    mapping = {}
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 2:
                continue
            pid = row[0].strip()
            fname = row[1].strip()
            mapping[pid] = fname
    return mapping


def main():
    parser = argparse.ArgumentParser(description="Assign images to products from file names")
    parser.add_argument('--dir', default=DEFAULT_DIR, help='directory containing image files')
    parser.add_argument('--map', help='CSV mapping file (product_id,filename)')

    args = parser.parse_args()
    img_dir = args.dir
    mapping = {}
    if args.map:
        mapping = load_mapping(args.map)
        print(f"Loaded {len(mapping)} entries from mapping file")

    # list files in directory
    if not os.path.isdir(img_dir):
        print(f"Image directory not found: {img_dir}")
        return

    files = os.listdir(img_dir)
    print(f"Found {len(files)} files in images directory")

    app = create_app()
    with app.app_context():
        products = Product.query.all()
        updates = 0
        for p in products:
            chosen = None
            # explicit mapping takes precedence
            if mapping and str(p.id) in mapping:
                fname = mapping[str(p.id)]
                if fname in files:
                    chosen = fname
                else:
                    print(f"mapping for {p.id} -> {fname} not found in directory")
            if not chosen:
                # attempt to match by slug of name
                slug = slugify(p.name or '')
                for f in files:
                    name_noext = os.path.splitext(f)[0]
                    if slug and slug in name_noext:
                        chosen = f
                        break
                # fallback: look for id in filename
                if not chosen:
                    for f in files:
                        if f.startswith(str(p.id) + '-') or f.endswith('-' + str(p.id) + os.path.splitext(f)[1]):
                            chosen = f
                            break
            if chosen:
                newpath = '/static/images/' + chosen
                if p.image != newpath:
                    print(f"Updating {p.id} '{p.name}' -> {chosen}")
                    p.image = newpath
                    updates += 1
            else:
                print(f"No matching image for product {p.id} '{p.name}'")
        if updates:
            db.session.commit()
            print(f"Committed {updates} updates to database")
        else:
            print("No updates necessary")

if __name__ == '__main__':
    main()
