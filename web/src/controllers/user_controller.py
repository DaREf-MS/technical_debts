"""
User management controller for admin operations
"""
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user
from src.app import app, db
from src.models.model import User, Repository, RepositoryAccess
from src.utilities.auth import admin_required, hash_password


@app.route('/admin/users')
@admin_required
def admin_users():
    """List all users"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@app.route('/admin/users/create', methods=['GET', 'POST'])
@admin_required
def admin_create_user():
    """Create a new user (admin only)"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        is_admin = request.form.get('is_admin') == 'on'
        
        # Validation
        if not username or not email or not password:
            flash('Please fill in all required fields.', 'danger')
            return render_template('admin/user_form.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('admin/user_form.html')
        
        # Check duplicates
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('admin/user_form.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('admin/user_form.html')
        
        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            is_admin=is_admin
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {username} created successfully!', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/user_form.html', user=None)


@app.route('/admin/users/<user_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(user_id):
    """Edit user details"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        is_admin = request.form.get('is_admin') == 'on'
        is_active = request.form.get('is_active') == 'on'
        new_password = request.form.get('new_password')
        
        # Check email uniqueness
        if email != user.email:
            if User.query.filter_by(email=email).first():
                flash('Email already registered.', 'danger')
                return render_template('admin/user_form.html', user=user)
        
        # Update user
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.is_admin = is_admin
        user.is_active = is_active
        
        # Update password if provided
        if new_password:
            if len(new_password) < 8:
                flash('Password must be at least 8 characters long.', 'danger')
                return render_template('admin/user_form.html', user=user)
            user.password_hash = hash_password(new_password)
        
        db.session.commit()
        flash(f'User {user.username} updated successfully!', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/user_form.html', user=user)


@app.route('/admin/users/<user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)
    
    # Prevent self-deletion
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin_users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {username} deleted successfully.', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/users/<user_id>/toggle-active', methods=['POST'])
@admin_required
def admin_toggle_user_active(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)
    
    # Prevent self-deactivation
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'danger')
        return redirect(url_for('admin_users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} {status} successfully.', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/repository-access')
@admin_required
def admin_repository_access():
    """Manage repository access for users"""
    repositories = Repository.query.all()
    users = User.query.filter_by(is_active=True).all()
    
    # Get all access grants
    access_grants = RepositoryAccess.query.all()
    
    return render_template('admin/repository_access.html', 
                         repositories=repositories, 
                         users=users,
                         access_grants=access_grants)


@app.route('/admin/repository-access/grant', methods=['POST'])
@admin_required
def admin_grant_repository_access():
    """Grant repository access to a user"""
    user_id = request.form.get('user_id')
    repository_id = request.form.get('repository_id')
    can_read = request.form.get('can_read') == 'on'
    can_write = request.form.get('can_write') == 'on'
    
    if not user_id or not repository_id:
        flash('Please select both user and repository.', 'danger')
        return redirect(url_for('admin_repository_access'))
    
    # Check if access already exists
    existing = RepositoryAccess.query.filter_by(
        user_id=user_id,
        repository_id=repository_id
    ).first()
    
    if existing:
        # Update existing access
        existing.can_read = can_read
        existing.can_write = can_write
        flash('Repository access updated.', 'success')
    else:
        # Create new access
        access = RepositoryAccess(
            user_id=user_id,
            repository_id=repository_id,
            can_read=can_read,
            can_write=can_write,
            granted_by_id=current_user.id
        )
        db.session.add(access)
        flash('Repository access granted.', 'success')
    
    db.session.commit()
    return redirect(url_for('admin_repository_access'))


@app.route('/admin/repository-access/<access_id>/revoke', methods=['POST'])
@admin_required
def admin_revoke_repository_access(access_id):
    """Revoke repository access"""
    access = RepositoryAccess.query.get_or_404(access_id)
    
    db.session.delete(access)
    db.session.commit()
    
    flash('Repository access revoked.', 'success')
    return redirect(url_for('admin_repository_access'))


@app.route('/api/users/<user_id>/repositories')
@admin_required
def api_user_repositories(user_id):
    """API endpoint to get user's repository access"""
    user = User.query.get_or_404(user_id)
    
    access_list = []
    for access in user.repository_access:
        access_list.append({
            'id': access.id,
            'repository_id': access.repository_id,
            'repository_name': f"{access.repository.owner}/{access.repository.name}",
            'can_read': access.can_read,
            'can_write': access.can_write,
            'granted_at': access.granted_at.isoformat()
        })
    
    return jsonify(access_list)
