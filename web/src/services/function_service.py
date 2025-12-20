import uuid
from flask import Flask
from flask import request, render_template, redirect, url_for, jsonify
import requests

from src.models import db
from src.models.model import *

def create_function(name, line_position, file_id):
    function = Function(
        id = str(uuid.uuid4()),
        name = name,
        line_position = line_position,
        file_id = file_id,
    )

    db.session.add(function)
    db.session.commit()

    return function


def get_function_by_name(name):
    return db.session.query(Function).filter_by(name=name).first()


def get_function_by_name_and_file(name: str, file_id: str):
    return (
        db.session.query(Function)
        .filter(Function.name == name, Function.file_id == file_id)
        .first()
    )
