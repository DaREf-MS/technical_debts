"""
Authentication controller for login, logout, register, and password reset
"""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from src.app import app, db
from src.models.model import User
from src.utilities.auth import hash_password, verify_password, generate_reset_token, verify_reset_token
from datetime import datetime, timedelta


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username_or_email = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        if not username_or_email or not password:
            flash('Please provide both username/email and password.', 'danger')
            return render_template('auth/login.html')
        
        # Try to find user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if not user or not verify_password(user.password_hash, password):
            flash('Invalid username/email or password.', 'danger')
            return render_template('auth/login.html')
        
        if not user.is_active:
            flash('Your account has been deactivated. Please contact an administrator.', 'danger')
            return render_template('auth/login.html')
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        login_user(user, remember=remember)
        flash(f'Welcome back, {user.first_name or user.username}!', 'success')
        
        # Redirect to next page or index
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('index'))
    
    return render_template('auth/login.html')


@app.route('/logout')
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        # Validation
        if not username or not email or not password:
            flash('Please fill in all required fields.', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('auth/register.html')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html')
        
        # Check if this is the first user - make them admin
        is_first_user = User.query.count() == 0
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            is_admin=is_first_user
        )
        
        db.session.add(user)
        db.session.commit()
        
        if is_first_user:
            flash('Account created successfully! You are now an administrator. Please log in.', 'success')
        else:
            flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html')


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Request password reset"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Please provide your email address.', 'danger')
            return render_template('auth/forgot_password.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate reset token
            token = generate_reset_token(email, app.config['SECRET_KEY'])
            user.reset_token = token
            user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            
            # In production, send email with reset link
            # For now, we'll just show a message
            reset_url = url_for('reset_password', token=token, _external=True)
            flash(f'Password reset link: {reset_url}', 'info')
            # TODO: Send email with reset_url
        
        # Always show success message to prevent email enumeration
        flash('If an account with that email exists, a password reset link has been sent.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/forgot_password.html')


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Verify token
    email = verify_reset_token(token, app.config['SECRET_KEY'], max_age=3600)
    
    if not email:
        flash('Invalid or expired reset link.', 'danger')
        return redirect(url_for('forgot_password'))
    
    user = User.query.filter_by(email=email, reset_token=token).first()
    
    if not user or user.reset_token_expiry < datetime.utcnow():
        flash('Invalid or expired reset link.', 'danger')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or not confirm_password:
            flash('Please fill in all fields.', 'danger')
            return render_template('auth/reset_password.html', token=token)
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/reset_password.html', token=token)
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('auth/reset_password.html', token=token)
        
        # Update password
        user.password_hash = hash_password(password)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()
        
        flash('Password has been reset successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/reset_password.html', token=token)
