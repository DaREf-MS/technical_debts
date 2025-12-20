import uuid
from flask import Flask
from flask import request, render_template, redirect, url_for, jsonify
import requests

from src.models import db
from src.models.model import *


def create_commit(commit_sha, commit_date, author, message, branch_id):
    commit = Commit(
        id = str(uuid.uuid4()),
        sha = commit_sha,
        date = commit_date,
        author = author,
        message = message,
        branch_id = branch_id,
    )

    db.session.add(commit)
    db.session.commit()

    return commit


def ensure_commit_exists_by_sha(commit, branch_id):
    found_commit = get_commit_by_sha(commit.get("sha"))
    if not found_commit:
        # no commit found, so we create it
        # Convert date string to datetime object - GitHub API returns ISO format
        commit_date = datetime.fromisoformat(commit.get("date").replace('Z', '+00:00'))
        created_commit = create_commit(
            commit.get("sha"), commit_date, commit.get("author"), commit.get("message"), branch_id
        )

        return created_commit
    
    return found_commit


def get_commit_by_commit_id(commit_id):
    return Commit.query.get(commit_id)


def get_commit_by_sha(commit_sha):
    return db.session.query(Commit).filter_by(sha=commit_sha).first()


def get_commits_by_branch_id(branch_id):
    commits = Commit.query.filter_by(branch_id=branch_id).order_by(Commit.date.desc()).all()

    return [commit.as_dict() for commit in commits]


def get_commits_by_branch_name(branch_name):
    branch = Branch.query.filter_by(branch_name=branch_name).first()

    commits = Commit.query.filter_by(branch_id=branch.id).order_by(Commit.date.desc()).all()

    return [commit.as_dict() for commit in commits]