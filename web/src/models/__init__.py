from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models after db is created to avoid circular imports
from src.models.model import (
    Repository, Branch, Commit, File, Function,
    IdentifiableEntity, FileIdentifiableEntity,
    Complexity, IdentifiableEntityCount
)

__all__ = [
    'db',
    'Repository', 'Branch', 'Commit', 'File', 'Function',
    'IdentifiableEntity', 'FileIdentifiableEntity',
    'Complexity', 'IdentifiableEntityCount'
]