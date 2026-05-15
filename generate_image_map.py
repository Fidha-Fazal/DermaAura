"""Generate CSV template mapping product ids to suggested image filenames.

This can help you rename/download images and then run `assign_images.py` with
that CSV. The output is written to stdout or to a file if specified.

Usage:
    python generate_image_map.py [--out map.csv]

The CSV will contain lines like:
    1,lakme-vitamin-c-serum-1.jpg
    2,mamaearth-salicylic-acid-cleanser-2.jpg

You can edit the filenames to match the actual files you downloaded.
"""

import argparse, re
from app import create_app
from models import Product


def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def main():
    parser = argparse.ArgumentParser(description="Generate product image mapping CSV")
    parser.add_argument('--out', help='output CSV file (defaults to stdout)')
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        products = Product.query.all()
        lines = []
        for p in products:
            fname = f"{slugify(p.name)}-{p.id}.jpg" if p.name else f"product-{p.id}.jpg"
            lines.append(f"{p.id},{fname}")

    content = "\n".join(lines)
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Wrote mapping to {args.out}")
    else:
        print(content)

if __name__ == '__main__':
    main()
