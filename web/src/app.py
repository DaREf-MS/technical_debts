from flask import Flask
from flask import request, render_template, redirect, url_for, jsonify
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from datetime import datetime, timedelta
import uuid

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Database configuration
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'postgres')
DATABASE_PORT = os.getenv('DATABASE_PORT', '5432')
DATABASE_HOST = os.getenv('DATABASE_HOST', 'postgres')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{POSTGRES_DB}'
app.config['SQLALCHEMY_ENABLE_POOL_PRE_PING'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from src.models import *
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from src.models.model import User
    try:
        return User.query.get(user_id)
    except Exception:
        # Table doesn't exist yet or database error
        return None

import src.services.repository_service as repository_service
import src.services.branch_service as branch_service

import src.controllers.identifiable_entity_controller
import src.controllers.commit_controller
import src.controllers.metrics_controller
import src.controllers.repository_controller
import src.controllers.task_controller  # Register task routes
import src.controllers.auth_controller  # Register auth routes
import src.controllers.user_controller  # Register user management routes

import src.services.metrics_service as metrics_service
from src.utilities.auth import login_required, repository_access_required


@app.route('/', methods=['GET'])
@login_required
def index():
    """
        Landing page
    """
    try:
        from flask_login import current_user
        from src.models.model import RepositoryAccess
        
        if current_user.is_admin:
            # Admins see all repositories
            repositories = repository_service.get_all_repositories()
        else:
            # Regular users see only repositories they have access to
            access_list = RepositoryAccess.query.filter_by(user_id=current_user.id).all()
            repositories = [access.repository for access in access_list if access.can_read]
    except Exception:
        repositories = []

    return render_template('index.html', repositories=repositories)


@app.route('/dashboard/<owner>/<name>/', methods=['GET'])
@login_required
@repository_access_required('read')
def dashboard(owner, name):
    """
        Return the dashboard for a repository. Repo needs to be created first.
    """
    try:
        repo = repository_service.get_repository_by_owner_and_name(owner, name)
        branches = branch_service.get_branches_by_repository_id(repo.id)

        return render_template('dashboard.html', repository=repo, branches=branches)
    except Exception as e:
        print(str(e))
        return render_template('dashboard.html', repository=None, branches=None)


@app.route('/debt_evolution/<owner>/<name>/', methods=['GET'])
@login_required
@repository_access_required('read')
def debt_evolution(owner, name):
    """
        Return the debt evolution page for a repository with Plotly visualization.
    """
    try:
        from src.services.task_manager import task_manager
        
        repo = repository_service.get_repository_by_owner_and_name(owner, name)
        branches = branch_service.get_branches_by_repository_id(repo.id)

        # Calculate default dates: today and 30 days prior
        today = datetime.now()
        thirty_days_ago = today - timedelta(days=30)
        
        # Format dates for the API (dd/mm/yyyy hh:mm)
        default_end_date = today.strftime('%d/%m/%Y 23:59')
        default_start_date = thirty_days_ago.strftime('%d/%m/%Y 00:00')

        # Get query parameters for date range and branch (with calculated defaults)
        start_date = request.args.get('start_date', default_start_date)
        end_date = request.args.get('end_date', default_end_date)
        branch_name = request.args.get('branch', 'main' if branches else None)
        task_id = request.args.get('task_id')  # Check if we're polling for results
        
        # Find the selected branch or use the first one
        selected_branch = None
        if branch_name:
            selected_branch = next((b for b in branches if b.name == branch_name), None)
        if not selected_branch and branches:
            selected_branch = branches[0]
            
        debt_data = []
        is_loading = False
        
        if selected_branch:
            # If we have a task_id, check if the task is complete
            if task_id:
                task = task_manager.get_task(task_id)
                if task:
                    if task.status == "completed":
                        # Use the result from the task
                        debt_data = task.result if task.result else []
                    elif task.status == "failed":
                        return render_template('debt_evolution.html', 
                            repository=repo, 
                            branches=branches, 
                            selected_branch=selected_branch,
                            error=f"Calculation failed: {task.error}",
                            start_date=start_date,
                            end_date=end_date)
                    else:
                        # Still loading
                        is_loading = True
                else:
                    # Task not found, may have been cleaned up - start new one
                    new_task_id = task_manager.create_task("debt_evolution")
                    
                    def _run_debt_calc(task_id, repo_id, branch_id, start_date, end_date):
                        return metrics_service.calculate_debt_evolution(
                            repo_id, branch_id, start_date, end_date, task_id
                        )
                    
                    task_manager.run_task_in_background(
                        new_task_id,
                        _run_debt_calc,
                        app,  # Pass Flask app for context
                        repo.id,
                        selected_branch.id,
                        start_date,
                        end_date
                    )
                    
                    # Redirect to same page with new task_id
                    return redirect(url_for('debt_evolution', 
                        owner=owner, 
                        name=name, 
                        task_id=new_task_id,
                        start_date=start_date,
                        end_date=end_date,
                        branch=selected_branch.name))
            else:
                # No task_id - check if we need to start a new calculation
                # For now, just calculate synchronously for small datasets or start async
                # We'll start it async and return loading state
                new_task_id = task_manager.create_task("debt_evolution")
                
                def _run_debt_calc(task_id, repo_id, branch_id, start_date, end_date):
                    return metrics_service.calculate_debt_evolution(
                        repo_id, branch_id, start_date, end_date, task_id
                    )
                
                task_manager.run_task_in_background(
                    new_task_id,
                    _run_debt_calc,
                    app,  # Pass Flask app for context
                    repo.id,
                    selected_branch.id,
                    start_date,
                    end_date
                )
                
                # Redirect to same page with task_id
                return redirect(url_for('debt_evolution', 
                    owner=owner, 
                    name=name, 
                    task_id=new_task_id,
                    start_date=start_date,
                    end_date=end_date,
                    branch=selected_branch.name))

        return render_template('debt_evolution.html', 
            repository=repo, 
            branches=branches, 
            selected_branch=selected_branch,
            debt_data=debt_data,
            start_date=start_date,
            end_date=end_date,
            task_id=task_id,
            is_loading=is_loading)
    except Exception as e:
        print(f"Error in debt_evolution: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template('debt_evolution.html', 
            repository=None, 
            branches=None, 
            error=str(e))

import src.services.identifiable_entity_service as identifiable_entity_service
# with app.app_context():
#   print('dropping...')
#   db.drop_all()
#   db.reflect()
#   db.create_all()
#   identifiable_entity_service.create_identifiable_entity("todo")
#   identifiable_entity_service.create_identifiable_entity("fixme")
#   db.session.commit()