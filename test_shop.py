import pytest

from models import Product
from app import db


def test_shop_page(client):
    # ensure the database has at least one product so /shop returns 200
    with client.application.app_context():
        if Product.query.count() == 0:
            db.session.add(Product(name='Dummy', category='skin', price=1.0))
            db.session.commit()
    resp = client.get('/shop')
    assert resp.status_code == 200
    assert b'Shop' in resp.data  # simple sanity check
