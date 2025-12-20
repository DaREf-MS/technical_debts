import uuid
import re

from src.models import db
from src.models.model import *


def create_identifiable_entity(name):
    indentifiable_entity = IdentifiableEntity(
        id = str(uuid.uuid4()),
        name = name,
    )

    db.session.add(indentifiable_entity)
    db.session.commit()

    return indentifiable_entity


def create_file_entity(identifiable_entity_id, file_id, line_position):
    file_entity = FileIdentifiableEntity(
        id = str(uuid.uuid4()),
        identifiable_entity_id = identifiable_entity_id,
        file_id = file_id,
        line_position = line_position,
    )

    db.session.add(file_entity)
    db.session.commit()

    return file_entity


def get_all_identifiable_entities():
    return IdentifiableEntity.query.all()


def get_identifiable_entity_by_name(name):
    return IdentifiableEntity.query.filter_by(name=name).first()


def get_identifiable_entity_by_file_id_verbose(file_id):
    verbose = []
    file_identities = FileIdentifiableEntity.query.filter_by(file_id=file_id).all()
    for file_identity in file_identities:
        file = File.query.get(file_identity.file_id)
        identity = IdentifiableEntity.query.get(file_identity.identifiable_entity_id)
        verbose.append({
            "file_name": file.name,
            "entity_name": identity.name,
            "line_position": file_identity.line_position,
        })

    return verbose


def get_file_entity_by_name(name):
    return FileIdentifiableEntity.query.filter_by(name=name).first()


def get_file_entity_by_name_and_file(name: str, file_id: str, line_position: int):
    return FileIdentifiableEntity.query.filter_by(name=name, file_id=file_id, line_position=line_position).first()


def search_identifable_entity(code, identifiable_entity):
    """
    Search for a string sequence in file content.
    
    Args:
        code: File content as string (from Lizard or other source)
        identifiable_entity: String sequence to search for
    
    Returns:
        List of objects with line numbers where the string was found
    """

    pattern = re.compile(rf'(?im)\b(?P<tag>{re.escape(identifiable_entity)})\b\s*:?\s*(?P<rest>.*)')
    findings = []
    for i, line in enumerate(code.splitlines(), start=1):

        m = pattern.search(line)
        if not m:
            # if not found then skip code and check next lines  
            continue

        findings.append(i)
    return findings