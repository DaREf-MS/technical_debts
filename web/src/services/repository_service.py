import uuid
from flask import Flask
from flask import request, render_template, redirect, url_for, jsonify
import requests

from src.models import db
from src.models.model import *

import src.services.github_service as github_service

def create_repository(owner, name):
    repository = Repository(
        id = str(uuid.uuid4()),
        owner = owner,
        name = name,
    )
    db.session.add(repository)
    db.session.commit()

    return repository


def get_all_repositories():
    return [repo.as_dict() for repo in db.session.query(Repository).all()]


def get_repository_by_owner_and_name(owner, name):
    return db.session.query(Repository).filter_by(owner=owner, name=name).first()


def get_repository_by_repository_id(id):
    return db.session.query(Repository).filter_by(id=id).first()


def get_repository_url_by_owner_and_name(owner, name):
    repo = db.session.query(Repository).filter_by(owner=owner, name=name).first()

    return f"https://github.com/{repo.owner}/{repo.name}.git"


def get_repository_url_by_repository_id(id):
    repo = db.session.query(Repository).filter_by(id=id).first()

    return f"https://github.com/{repo.owner}/{repo.name}.git"
