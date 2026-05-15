import sys
sys.path.insert(0, '.')
from app import app, db
from models import User, Product, Wishlist

def run():
    with app.test_client() as client:
        with app.app_context():
            Wishlist.query.delete()
            Product.query.delete()
            User.query.delete()
            
            user = User(username='testuser', email='test@example.com', detected_skin_type='Oily')
            user.set_password('password123')
            db.session.add(user)
            
            product = Product(name='Test Serum', category='skin', price=100.0)
            db.session.add(product)
            db.session.commit()
            
            user_id = user.id
            product_id = product.id

        print("Testing Profile and Wishlist endpoints...")
        
        client.post('/login', data={'email': 'test@example.com', 'password': 'password123'})
        
        resp = client.get('/profile')
        assert resp.status_code == 200
        
        with client.session_transaction() as sess:
            sess['_csrf_token'] = 'token'
            
        resp = client.post('/wishlist/add', json={'product_id': product_id}, headers={'X-CSRF-Token': 'token'})
        assert resp.status_code == 200

        resp = client.get('/wishlist')
        assert resp.status_code == 200
        assert b'Test Serum' in resp.data

        resp = client.post('/wishlist/remove', json={'product_id': product_id}, headers={'X-CSRF-Token': 'token'})
        assert resp.status_code == 200

        resp = client.get('/wishlist')
        assert resp.status_code == 200

        print("✓ All tests passed successfully.")

if __name__ == '__main__':
    run()
