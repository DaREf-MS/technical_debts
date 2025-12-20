import uuid
from flask import Flask
from flask import request, render_template, redirect, url_for, jsonify
import requests

from src.models import db
from src.models.model import *

import src.services.github_service as github_service


def create_file(name, commit_id):
    file = File(
        id = str(uuid.uuid4()),
        name = name,
        commit_id = commit_id,
    )

    db.session.add(file)
    db.session.commit()

    return file


def get_file_by_filename(name):
    return db.session.query(File).filter_by(name=name).first()


def get_file_by_filename_and_commit(filename: str, commit_id: str):
    return (
        db.session.query(File)
        .filter(File.name == filename, File.commit_id == commit_id)
        .first()
    )


def get_files_by_commit_id(commit_id):
    files = File.query.filter_by(commit_id=commit_id).all()

    return files