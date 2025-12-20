from flask import request, jsonify

from src.app import app

import src.services.commit_service as commit_service

@app.route('/api/get_commits_by_branch_name', methods=['POST'])
def get_commits_by_branch_name():
    """
        Gets a list of commits by the name of a branch

        @param branch_name: Name of the branch
    """

    data = request.get_json()
    branch_name = data.get('branch_name')

    try:
        commits = commit_service.get_commits_by_branch_name(branch_name)
    except Exception:
        commits = []

    return jsonify(commits)


@app.route('/api/get_commits_by_branch_id', methods=['POST'])
def get_commits_by_branch_id():
    """
        Gets a list of commits by the ID of a branch

        @param branch_id: ID of the branch
    """

    data = request.get_json()
    branch_id = data.get('branch_id')

    try:
        commits = commit_service.get_commits_by_branch_id(branch_id)
    except Exception:
        commits = []

    return jsonify(commits)