from src.utilities.json_encoder import JsonEncoder
from dataclasses import dataclass

@dataclass
class EntityReport(JsonEncoder.Interface):
    _FIELDS = {"file_name", "entity_name", "line_position"}
    file_name : str = ""
    entity_name : str = ""
    line_position : int = 0

    def _validate_keys(self, entities : dict):
        for key in EntityReport._FIELDS:
            assert key in entities   # validates that the dict contains expected keys. 
            continue

    def load(self, entities): 
        assert type(entities) == dict
        
        self._validate_keys(entities)
        for key in EntityReport._FIELDS:
            setattr(self, key, entities[key])
            continue
        
        return self