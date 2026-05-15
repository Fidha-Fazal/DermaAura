import os
import io
from app import create_app, db  # type: ignore
from models import User, Product  # type: ignore

app = create_app()

def run_tests():
    with app.test_client() as client:
        with app.app_context():
            print("--- Testing App Initialization ---")
            assert app is not None
            
            # Create a test product if none exists
            if not Product.query.first():
                p = Product(name='Test Serum', category='skin', price=499.0, description='A test serum.')
                db.session.add(p)
                db.session.commit()
            product = Product.query.first()
            p_id = product.id
            
            print("--- Testing Registration ---")
            # Register a user
            test_email = 'test_verify@example.com'
            user = User.query.filter_by(email=test_email).first()
            if user:
                db.session.delete(user)
                db.session.commit()
            
            res = client.post('/register', data={
                'full_name': 'Test User',
                'email': test_email,
                'password': 'password123',
                'confirm_password': 'password123'
            }, follow_redirects=True)
            assert res.status_code == 200
            print("Registration OK")
            
            print("--- Testing Login ---")
            client.get('/logout', follow_redirects=True)
            res = client.post('/login', data={
                'email': test_email,
                'password': 'password123'
            }, follow_redirects=True)
            assert res.status_code == 200
            
            # Verify session has user
            with client.session_transaction() as sess:
                assert sess.get('user_id') is not None
                csrf_token = sess.get('_csrf_token')
            print("Login OK")
            
            print("--- Testing Cart ---")
            res = client.post('/add-to-cart', json={
                'product_id': p_id,
                'qty': 2
            }, headers={'X-CSRF-Token': csrf_token})
            assert res.status_code == 200
            assert 'added' in res.get_json()['message']
            print("Add to cart OK")
            
            print("--- Testing Checkout Flow ---")
            res = client.get('/checkout', follow_redirects=True)
            assert res.status_code == 200
            
            # Submit checkout form
            res = client.post('/checkout', data={
                'line1': '123 Test St',
                'city': 'Mumbai',
                'state': 'MH',
                'zip_code': '400001',
                'payment_method': 'cod'
            }, follow_redirects=True)
            assert res.status_code == 200
            
            print("--- Testing AI Scanner Route (GET) ---")
            res = client.get('/analyze', follow_redirects=True)
            assert res.status_code == 200
            print("Analyze route OK")
            
            print("ALL CORE FLOWS VERIFIED SUCCESSFULLY!")

if __name__ == '__main__':
    run_tests()
