import pytest
from models import User, Product, Order, Payment, Wishlist
from app import db
from io import BytesIO
from PIL import Image
from flask import current_app
import os


def login_as(client, email, password):
    return client.post('/login', data={'email': email, 'password': password}, follow_redirects=True)


def test_checkout_and_admin_flow(client):
    # create initial data – the test fixture has already reset the database
    with client.application.app_context():
        # create a normal user
        u = User(username='Test User', email='user@test.com')
        u.set_password('pass123')
        db.session.add(u)
        db.session.commit()
        user_id = u.id

        # create a sample product
        p = Product(name='Sample', category='skin', price=100.0)
        db.session.add(p)
        db.session.commit()
        pid = p.id

    # simulate login by setting user in session
    with client.session_transaction() as sess:
        sess['user_id'] = user_id
        sess['user_name'] = 'Test User'
        sess['_csrf_token'] = 'token123'

    # add product to cart in session
    with client.session_transaction() as sess:
        sess['cart'] = {str(pid): 2}

    # perform checkout POST
    resp = client.post('/checkout', data={
        'line1': 'Address1',
        'city': 'City',
        'state': 'State',
        'zip_code': '12345',
        'country': 'India',
        'payment_method': 'card'
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Order' in resp.data

    # verify order & payment in database
    with client.application.app_context():
        order = Order.query.first()
        assert order is not None
        assert order.payment_status == 'Success'
        assert order.status == 'Paid'
        assert order.payment is not None
        assert order.payment.method.lower() == 'card'
        assert order.total_price > 0

    # quick view JSON endpoint should return basic product info
    with client.application.app_context():
        prod = Product.query.first()
        pid = prod.id
    resp_quick = client.get(f'/product/{pid}?json=1')
    assert resp_quick.status_code == 200
    jq = resp_quick.get_json()
    assert jq['id'] == pid
    assert 'name' in jq and 'price' in jq

    # simulate pay_simulate should also work (even if already paid)
    resp2 = client.post('/pay/simulate', json={'order_id': order.order_id})
    assert resp2.status_code == 200

    # wishlist operations
    with client.session_transaction() as sess:
        sess['cart'] = {}
        sess['_csrf_token'] = 'tok'
        sess['user_id'] = user_id
        sess['user_name'] = 'Test User'
    resp_wl = client.post('/wishlist/add', json={'product_id': pid}, headers={'X-CSRF-Token': 'tok'})
    assert resp_wl.status_code == 200
    with client.application.app_context():
        wl = Wishlist.query.filter_by(user_id=user_id, product_id=pid).first()
        assert wl is not None

    # create admin user and login
    with client.application.app_context():
        admin = User(username='Admin', email='admin@test.com', role='admin')
        admin.set_password('adminpass')
        db.session.add(admin)
        db.session.commit()
    resp3 = client.post('/admin/login', data={'email': 'admin@test.com', 'password': 'adminpass'})
    assert resp3.status_code == 302 or resp3.status_code == 200

    # admin orders page should include the shipping address
    resp_admin = client.get('/admin/orders')
    assert resp_admin.status_code == 200
    assert b'Address1' in resp_admin.data

    # update order status via admin endpoint
    with client.application.app_context():
        oid = order.id
    resp4 = client.post(f'/admin/orders/{oid}/update', data={'status': 'Shipped'}, follow_redirects=True)
    assert resp4.status_code == 200
    with client.application.app_context():
        order = Order.query.get(oid)
        assert order.status == 'Shipped'

    # admin can add a product via the new-product route using text field
    resp5 = client.post('/admin/products/new', data={
        'name': 'TestProd',
        'category': 'skin',
        'price': 123.45,
        'description': 'desc',
        'rating': 4.2,
        'image': 'foo.jpg'
    }, follow_redirects=True)
    assert resp5.status_code == 200
    with client.application.app_context():
        p = Product.query.filter_by(name='TestProd').first()
        assert p is not None
        assert p.image_url == 'foo.jpg'

    # now verify upload via file works too
    # create a real PNG bytes buffer
    from io import BytesIO
    from PIL import Image
    buf = BytesIO()
    Image.new('RGB', (120,120), color='blue').save(buf, 'PNG')
    buf.seek(0)

    resp6 = client.post('/admin/products/new', data={
        'name': 'FileProd',
        'category': 'hair',
        'price': 50,
        'description': 'descfile',
        'rating': 4.0,
        'image_file': (buf, 'upload.png')
    }, content_type='multipart/form-data', follow_redirects=True)
    assert resp6.status_code == 200
    with client.application.app_context():
        fp = Product.query.filter_by(name='FileProd').first()
        assert fp is not None
        # image_url should be generated filename not the literal 'upload.png'
        assert fp.image_url and fp.image_url.endswith('.png') and fp.image_url != 'upload.png'
        import os
        dest = os.path.join(current_app.root_path, 'static', 'images', fp.image_url)
        assert os.path.exists(dest), 'uploaded file not saved'

    # edit the first TestProd using a new upload
    with client.application.app_context():
        pid = p.id
    buf2 = BytesIO()
    Image.new('RGB', (150,150), color='green').save(buf2, 'PNG')
    buf2.seek(0)
    resp7 = client.post(f'/admin/products/{pid}/edit', data={
        'name': 'TestProd2',
        'category': 'skin',
        'price': 200,
        'description': 'desc2',
        'rating': 3.3,
        'image_file': (buf2, 'new.png')
    }, content_type='multipart/form-data', follow_redirects=True)
    assert resp7.status_code == 200
    with client.application.app_context():
        p2 = Product.query.get(pid)
        assert p2.name == 'TestProd2'
        assert p2.image_url.endswith('.png')


def test_stripe_session(client, monkeypatch):
    # setup fresh data for stripe session test
    with client.application.app_context():
        u = User(username='StripeUser', email='stripe@test.com')
        u.set_password('pw')
        db.session.add(u)
        db.session.commit()
        user_id = u.id

        p = Product(name='StripeProd', category='skin', price=50.0)
        db.session.add(p)
        db.session.commit()
        pid = p.id

    # simulate login/cart
    with client.session_transaction() as sess:
        sess['user_id'] = user_id
        sess['user_name'] = 'StripeUser'
        sess['_csrf_token'] = 't'
        sess['cart'] = {str(pid): 1}

    # case 1: no stripe keys -> simulated response
    monkeypatch.delenv('STRIPE_SECRET_KEY', raising=False)
    monkeypatch.delenv('STRIPE_PUBLISHABLE_KEY', raising=False)
    resp = client.post('/create-checkout-session')
    assert resp.status_code == 200
    j = resp.get_json()
    assert j.get('simulated') is True

    # case 2: provide keys and mock stripe API
    monkeypatch.setenv('STRIPE_SECRET_KEY', 'sk_test_key')
    monkeypatch.setenv('STRIPE_PUBLISHABLE_KEY', 'pk_test_key')
    import stripe
    class DummySession:
        @staticmethod
        def create(**kwargs):
            class R:
                id = 'sess_dummy'
            return R()
    monkeypatch.setattr(stripe.checkout, 'Session', DummySession)

    resp2 = client.post('/create-checkout-session')
    assert resp2.status_code == 200
    j2 = resp2.get_json()
    assert j2.get('id') == 'sess_dummy'
    assert j2.get('publishable') == 'pk_test_key'
