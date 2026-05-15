"""Development seed script: create admin user and a few products if missing."""
from app import create_app, db
from models import User, Product

app = create_app()
with app.app_context():
    # create tables
    db.create_all()

    if not User.query.filter_by(email='admin@test.com').first():
        admin = User(username='Administrator', email='admin@test.com', role='admin')
        admin.set_password('testpass123')
        db.session.add(admin)
        print('Created admin user admin@test.com / testpass123')
    else:
        print('Admin already exists')

    # sample products
    samples = [
        {'name': 'Hydrating Cream', 'category': 'skin', 'price': 299.0},
        {'name': 'Anti-dandruff Shampoo', 'category': 'hair', 'price': 199.0},
        {'name': 'Sunscreen', 'category': 'skin', 'price': 349.0},
    ]
    for item in samples:
        if not Product.query.filter_by(name=item['name']).first():
            p = Product(name=item['name'], category=item['category'], price=item['price'])
            db.session.add(p)
            print('Added product', item['name'])
    db.session.commit()
    print('Seeding complete')
