import requests

from flask import request, redirect, url_for
from flask_login import current_user
from src.app import app, db
from src.utilities.auth import login_required
from src.models.model import RepositoryAccess

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

import src.services.repository_service as repository_service
import src.services.branch_service as branch_service
import src.services.github_service as github_service
import src.services.commit_service as commit_service


@app.route('/create_repository', methods=['POST'])
@login_required
def create_repository():
    """
        Create a new repository

        :param owner: Github username of the repository owner
        :param repo: Github repository name
    """

    owner = request.form.get('owner')
    name = request.form.get('name')

    
    # store the repo
    repo = repository_service.create_repository(owner, name)

    # Grant the creator automatic access to the repository (unless admin)
    if not current_user.is_admin:
        access = RepositoryAccess(
            user_id=current_user.id,
            repository_id=repo.id,
            can_read=True,
            can_write=True,
            granted_by_id=current_user.id
        )
        db.session.add(access)
        db.session.commit()

    # store all the branches
    branches = branch_service.create_branches_from_repository(repo.id)

    # store the commits for the 10 latest commits
    for branch in branches:
        commits = github_service.get_latest_commits(owner, name, branch.name)

        for commit in commits:
            sha = commit.get('hash')
            date = datetime.fromisoformat(commit.get('date'))
            author = commit.get('author')
            message = commit.get('message')
            commit_service.create_commit(sha, date, author, message, branch.id)
    
            

    # Redirect to the repository dashboard after creating it
    return redirect(url_for('dashboard', owner=owner, name=name))