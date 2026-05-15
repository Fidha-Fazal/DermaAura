#!/usr/bin/env python3
"""
Create or promote an admin user for DermaAura.
Usage:
  python create_admin.py --email admin@example.com --password secret123 --name "Admin Name"
You can also set environment variables ADMIN_EMAIL and ADMIN_PASSWORD.
"""
import os
import argparse
from app import create_app, db
from models import User


def main():
    parser = argparse.ArgumentParser(description='Create or promote an admin user')
    parser.add_argument('--email', help='Admin email', default=os.getenv('ADMIN_EMAIL'))
    parser.add_argument('--password', help='Admin password', default=os.getenv('ADMIN_PASSWORD'))
    parser.add_argument('--name', help='Full name', default=os.getenv('ADMIN_NAME', 'Admin'))
    args = parser.parse_args()

    if not args.email or not args.password:
        parser.error('Please provide --email and --password (or set ADMIN_EMAIL/ADMIN_PASSWORD env vars)')

    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email=args.email).first()
        if user:
            user.is_admin = True
            # update password if desired
            user.set_password(args.password)
            db.session.commit()
            print(f"Promoted existing user '{user.full_name}' ({user.email}) to admin.")
        else:
            user = User(full_name=args.name, email=args.email)
            user.set_password(args.password)
            user.is_admin = True
            db.session.add(user)
            db.session.commit()
            print(f"Created new admin user '{user.full_name}' ({user.email}).")


if __name__ == '__main__':
    main()
