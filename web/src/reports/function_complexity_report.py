from src.utilities.json_encoder import JsonEncoder
from dataclasses import dataclass

@dataclass
class FunctionComplexityReport(JsonEncoder.Interface): 
    _FIELDS = {"file", "function", "start_line", "cyclomatic_complexity"}
    file : str = ""
    function : str = ""
    start_line : int = 0
    cyclomatic_complexity : int = 0

    def _validate_keys(self, func : dict):
        for key in FunctionComplexityReport._FIELDS:
            assert key in func   # validates that the dict contains expected keys. 
            continue

    def load(self, func : dict):
        assert type(func) == dict

        self._validate_keys(func)
        for key in FunctionComplexityReport._FIELDS:
            setattr(self, key, func[key])
            continue
        
        return self

        