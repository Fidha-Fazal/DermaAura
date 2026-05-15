import sys
sys.path.insert(0, '.')
from app import app, db
from models import User, Product, Review

def run():
    with app.test_client() as client:
        with app.app_context():
            Review.query.delete()
            Product.query.delete()
            User.query.delete()
            
            user = User(username='reviewer', email='review@example.com')
            user.set_password('password123')
            db.session.add(user)
            
            product = Product(name='Test Moisture', category='skin', price=50.0)
            db.session.add(product)
            db.session.commit()
            
            product_id = product.id

        print("Testing Reviews...")
        client.post('/login', data={'email': 'review@example.com', 'password': 'password123'})
        
        # Add 3 star review
        with client.session_transaction() as sess:
            sess['_csrf_token'] = 'token'
            
        resp = client.post(f'/product/{product_id}/review', data={
            'rating': '3',
            'comment_text': 'Average product.',
            'csrf_token': 'token'
        })
        
        with app.app_context():
            product_check = db.session.get(Product, product_id)
            assert product_check.rating == 3.0, f"Expected 3.0, got {product_check.rating}"
            
        print("✓ Verified average rating dynamically updates gracefully.")

if __name__ == '__main__':
    run()
