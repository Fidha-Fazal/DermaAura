from app import create_app
from models import User

app = create_app()
with app.app_context():
    admins = User.query.filter_by(role='admin').all()
    print('admin count:', len(admins))
    for a in admins:
        print('email:', a.email, 'username:', a.username, 'pw_hash:', a.password_hash)