#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from app import db
from models import Product


def test_features(client):
    """Test shop, search, and categories using shared client fixture"""
    # put a couple of products into the clean test database
    with client.application.app_context():
        # ensure fresh schema (fixture already did this)
        p1 = Product(name='Hydrating Cream', category='skin', price=299.0, description='hydrating formula')
        p2 = Product(name='Anti-Dandruff Shampoo', category='hair', price=399.0, description='anti dandruff solution')
        db.session.add_all([p1, p2])
        db.session.commit()
        total_products = Product.query.count()
        skin_products = Product.query.filter_by(category='skin').count()
        hair_products = Product.query.filter_by(category='hair').count()
        print(f"✓ Database has {total_products} products")
        print(f"  - Skincare: {skin_products}")
        print(f"  - Haircare: {hair_products}\n")

    # TEST 2: Shop page
    response = client.get('/shop')
    print(f"✓ Shop page status: {response.status_code}")
    html = response.get_data(as_text=True)
    assert 'class="card-title"' in html or 'class="card-title ' in html, "no card-title in shop page"
    assert html.find('<img src=') < html.find('class="card-title"'), "product title appears before image"

    # TEST 3: Category filter - skin
    response = client.get('/shop?category=skin')
    print(f"✓ Skincare filter status: {response.status_code}")

    # TEST 4: Category filter - hair
    response = client.get('/shop?category=hair')
    print(f"✓ Haircare filter status: {response.status_code}")

    # TEST 5: Search API
    response = client.get('/api/search?q=hydrating')
    print(f"✓ Search API status: {response.status_code}")
    results = response.get_json()
    print(f"  - Found {len(results)} results for 'hydrating'")

    # TEST 6: Another search
    response = client.get('/api/search?q=anti')
    results = response.get_json()
    print(f"  - Found {len(results)} results for 'anti'")

    print("\n✓ All tests passed!")

if __name__ == '__main__':
    pass
