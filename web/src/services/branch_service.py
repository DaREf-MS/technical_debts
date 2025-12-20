import uuid

from src.models import db
from src.models.model import *

import src.services.github_service as github_service


def create_branches_from_repository(repository_id):
    repo = db.session.query(Repository).get(repository_id)

    branches = github_service.fetch_branches(repo.owner, repo.name)

    branch_objs = []
    for branch in branches:
        branch_obj = Branch(
            id = str(uuid.uuid4()),
            repository_id = repo.id,
            name = branch,
        )

        db.session.add(branch_obj)
        db.session.commit()
        branch_objs.append(branch_obj)

    return branch_objs


def get_branch_by_branch_id(id):
    return db.session.query(Branch).filter_by(id=id).first()


def get_branches_by_repository_id(repository_id):
    return db.session.query(Branch).filter_by(repository_id=repository_id).all()
