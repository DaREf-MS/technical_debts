"""
Authentication utilities for user management and security
"""
from functools import wraps
from flask import redirect, url_for, flash, session, request
from flask_login import current_user
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash
import os


def hash_password(password):
    """Hash a password for storing"""
    return generate_password_hash(password)


def verify_password(password_hash, password):
    """Verify a stored password against one provided by user"""
    return check_password_hash(password_hash, password)


def generate_reset_token(email, secret_key, salt='password-reset-salt'):
    """Generate a password reset token"""
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(email, salt=salt)


def verify_reset_token(token, secret_key, salt='password-reset-salt', max_age=3600):
    """Verify a password reset token (default 1 hour expiry)"""
    serializer = URLSafeTimedSerializer(secret_key)
    try:
        email = serializer.loads(token, salt=salt, max_age=max_age)
        return email
    except Exception:
        return None


def login_required(f):
    """Decorator to require login for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        if not current_user.is_active:
            flash('Your account has been deactivated.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin access for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        if not current_user.is_active:
            flash('Your account has been deactivated.', 'danger')
            return redirect(url_for('login'))
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def repository_access_required(access_type='read'):
    """Decorator to check if user has access to a repository"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login', next=request.url))
            
            # Admin has access to everything
            if current_user.is_admin:
                return f(*args, **kwargs)
            
            # Get repository from URL parameters
            owner = kwargs.get('owner') or request.args.get('owner')
            name = kwargs.get('name') or request.args.get('name')
            
            if not owner or not name:
                flash('Repository not specified.', 'danger')
                return redirect(url_for('index'))
            
            # Check repository access
            from src.models.model import Repository, RepositoryAccess
            repo = Repository.query.filter_by(owner=owner, name=name).first()
            
            if not repo:
                flash('Repository not found.', 'danger')
                return redirect(url_for('index'))
            
            access = RepositoryAccess.query.filter_by(
                user_id=current_user.id,
                repository_id=repo.id
            ).first()
            
            if not access:
                flash('You do not have access to this repository.', 'danger')
                return redirect(url_for('index'))
            
            if access_type == 'write' and not access.can_write:
                flash('You do not have write access to this repository.', 'danger')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
