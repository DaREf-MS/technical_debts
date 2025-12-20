from flask import request, jsonify

from src.app import app

import src.services.identifiable_entity_service as identifiable_entity_service


@app.route('/api/create_identifiable_entity', methods=['POST'])
def create_identifiable_entity():
    """
        Gets a list of all the identifiable identities available

        @param name: name of the identity
    """

    data = request.get_json()
    name = data.get('name')

    try:
        identifiable_entity = identifiable_entity_service.create_identifiable_entity(name)
    except Exception:
        identifiable_entity = {}

    return identifiable_entity.as_dict()


@app.route('/api/get_all_identifiable_entities', methods=['POST'])
def get_all_identifiable_entities():
    """
        Gets a list of all the identifiable identities available
    """

    try:
        identifiable_entities = identifiable_entity_service.get_all_identifiable_entities()
    except Exception:
        identifiable_entities = []

    return jsonify(identifiable_entities)
    