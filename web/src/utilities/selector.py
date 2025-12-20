from typing import Callable, Generic, TypeVar
from collections.abc import Iterable

TKey = TypeVar('TKey')
TValue = TypeVar('TValue')

class Selector(Generic[TKey, TValue]):
    """
    This class is a special iterator: it lets you select a value contained in 
    a class instance, allowing you to use a collection of class instances in 
    utility functions, such as `statistics.median()`. 

    ```
    class ComplexClass:
        a : int
        b : int
        c : str

    cc_list = [ComplexClass(1, 2, 3), ComplexClass(4, 5, 6)]
    selector = Selector(cc_list, lambda cc: cc.a)
    median = statistics.median(selector) # as if your list of class 
                                         # instances was a list of ints!
    """
    _func : Callable[[TKey], TValue]
    _it : object

    def __init__(self, iterable : Iterable, func : Callable[[TKey], TValue]): 
        self._func = func
        self._it = iter(iterable)
        return
    
    def __iter__(self):
        return self
    
    def __next__(self) -> TValue:
        key = next(self._it)
        val = self._func(key)
        return val