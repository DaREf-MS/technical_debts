from src.utilities.json_encoder import JsonEncoder
from typing import TypeVar, Generic

Ta = TypeVar('Ta')
Tb = TypeVar('Tb')

class Pair(Generic[Ta, Tb], JsonEncoder.Interface):
    first : Ta
    second : Tb

    def __init__(self, first : Ta, second : Tb):
        self.first = first
        self.second = second

    def as_tuple(self) -> tuple[Ta, Tb]: 
        return (self.first, self.second)
    
    def encode(self):
        _tuple = self.as_tuple()
        return JsonEncoder.breakdown(_tuple)