"""
Utility script to make first/any user an admin
Usage: python make_admin.py <email>
Example: python make_admin.py admin@example.com
"""
import sys
from app import create_app, db
from models import User

if __name__ == '__main__':
    app = create_app()
    
    if len(sys.argv) < 2:
        print("Usage: python make_admin.py <email>")
        print("Example: python make_admin.py admin@example.com")
        sys.exit(1)
    
    email = sys.argv[1]
    
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"User with email '{email}' not found!")
            sys.exit(1)
        
        user.role = 'admin'
        db.session.commit()
        print(f"User '{user.username}' ({email}) is now an admin!")
