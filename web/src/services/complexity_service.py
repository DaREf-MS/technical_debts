import uuid
from flask import Flask
from flask import request, render_template, redirect, url_for, jsonify
import requests

from src.models import db
from src.models.model import *


def create_complexity(value, function_id):
    complexity = Complexity(
        id = str(uuid.uuid4()),
        value = value,
        function_id = function_id,
    )

    db.session.add(complexity)
    db.session.commit()

    return complexity


def get_complexity_by_file_id_verbose(file_id):
    file = File.query.get(file_id)
    functions = Function.query.filter_by(file_id=file_id).all()

    complixities = []
    for function in functions:
        complexity = Complexity.query.filter_by(function_id=function.id).first()
        complixities.append({
            "file": file.name,
            "function": function.name,
            "start_line": function.line_position,
            "cyclomatic_complexity": complexity.value,
        })

    return complixities