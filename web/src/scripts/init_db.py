"""
Database initialization script
Creates tables and optionally creates an initial admin user
"""
import os
import sys

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import app, db
from src.models.model import User
from src.utilities.auth import hash_password


def init_db():
    """Initialize database tables"""
    print("Creating database tables...")
    with app.app_context():
        db.create_all()
        print("✓ Database tables created successfully!")


def create_admin_user():
    """Create initial admin user"""
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(username='admin').first()
        
        if admin:
            print("⚠ Admin user already exists!")
            return
        
        # Get admin credentials
        print("\n=== Create Admin User ===")
        username = input("Username (default: admin): ").strip() or "admin"
        email = input("Email: ").strip()
        
        while not email:
            print("Email is required!")
            email = input("Email: ").strip()
        
        password = input("Password (min 8 chars): ").strip()
        
        while len(password) < 8:
            print("Password must be at least 8 characters!")
            password = input("Password (min 8 chars): ").strip()
        
        first_name = input("First name (optional): ").strip() or None
        last_name = input("Last name (optional): ").strip() or None
        
        # Create admin user
        admin = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            is_admin=True
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"\n✓ Admin user '{username}' created successfully!")


if __name__ == '__main__':
    print("Technical Debt Analyzer - Database Initialization\n")
    
    # Initialize database
    init_db()
    
    # Create admin user
    create_admin = input("\nCreate admin user? (y/n): ").strip().lower()
    
    if create_admin == 'y':
        create_admin_user()
    
    print("\n✓ Database initialization complete!")
