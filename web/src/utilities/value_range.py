from typing import TypeVar, Generic
from src.utilities.json_encoder import JsonEncoder

T = TypeVar('T')

class ValueRange(Generic[T], JsonEncoder.Interface): 
    From : T
    To : T

    def __init__(self, From : T, To : T):
        self.From = From
        self.To = To
    
    def is_value_within(self, val : T) -> bool:
        return self.From <= val and val <= self.To
    
    def as_dict(self): 
        return {
            "From": self.From,
            "To": self.To
        }
    
    def encode(self):
        _dict = self.as_dict()
        return JsonEncoder.breakdown(_dict)

