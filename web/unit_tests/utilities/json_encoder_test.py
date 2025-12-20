from src.utilities.json_encoder import JsonEncoder
from enum import Enum

class DummyEnum(Enum):
    A = 1
    B = 2

class DummyClass(JsonEncoder.Interface):
    a : int
    b : float
    c : str
    d : DummyEnum

    def __init__(self, a : int, b : float, c : str, d = DummyEnum.A): 
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        return

def test__enum_to_raw():
    # arrange
    e = DummyEnum.A

    # act
    result = JsonEncoder._enum_to_raw(e)

    # assert 
    assert type(result) == list
    assert len(result) == 2
    assert result[0] == DummyEnum.A.name
    assert result[1] == DummyEnum.A.value

def test__dict_to_raw(): 
    # arrange
    _dict = {"A": 1, 14: "b"}

    # act
    result = JsonEncoder._dict_to_raw(_dict)

    # assert
    assert type(result) == dict
    assert len(result) == 2
    assert result["A"] == 1
    assert result[14] == "b"

def test_():
    # arrange
    class ABC:
        a : int
        b : range
        c : str

    abc = ABC()
    abc.a = 0
    abc.b = range(0, 10)
    abc.c = ""

    # act
    try:
        JsonEncoder._object_to_raw(abc)
    
    # assert 
        assert False
    except Exception as e:
        assert True
    return

def test__dict_to_raw__invalid_key_exception():
     # arrange
    dummy = DummyClass(2, 3.0, "s")
    _dict = {dummy: "a"}

    # act
    try:
        result = JsonEncoder._dict_to_raw(_dict)
    
    # assert
        assert False
    except Exception:
        assert True
        
def test__list_to_raw():
     # arrange
    _list = [1, 2]

    # act
    result = JsonEncoder._list_to_raw(_list)

    # assert
    assert type(result) == list
    assert len(result) == 2
    assert result[0] == 1
    assert result[1] == 2

def test__tuple_to_raw():
    # arrange
    _tuple = (1, 'A')

    # act
    result = JsonEncoder._tuple_to_raw(_tuple) 

    # assert
    assert type(result) == list # tuples are not supported by JSON, 
                                # encoder turns tuples into lists instead.
    assert len(result) == 2
    assert result[0] == 1
    assert result[1] == 'A'

def test__set_to_raw():
    # arrange
    _set = {1, 'A'}

    # act
    result = JsonEncoder._set_to_raw(_set) 

    # assert
    assert type(result) == list # sets are not supported by JSON, 
                                # encoder turns sets into lists instead.
    assert len(result) == 2
    assert result[0] == 1 or result[0] == 'A'  # order is not preserved or guaranteed by set. 
    assert result[1] == 'A' or result[1] == 1  

def test__object_to_raw__extends_interface():
    # arrange
    obj = DummyClass(3, 4.0, "d")

    # act
    result = JsonEncoder._object_to_raw(obj)

    # assert
    assert type(result) == dict 
    assert len(result) == 4
    assert result["a"] == 3
    assert result["b"] == 4.0
    assert result["c"] == "d"

    assert type(result["d"]) == list
    assert result["d"][0] == DummyEnum.A.name
    assert result["d"][1] == DummyEnum.A.value

def test__object_to_raw__is_primitive():
    # arrange
    obj = "hello"

    # act
    results = JsonEncoder._object_to_raw(obj)
    
    # assert
    assert type(results) == str

def test__object_to_raw__is_None():
    # arrange
    obj = None

    # act
    result = JsonEncoder._object_to_raw(obj)
    
    # assert
    assert result == None

def test_dump():
    # arrange
    obj = DummyClass(3, 4.0, "d")

    # act
    result = JsonEncoder.dump(obj)

    # assert
    assert result == '{"a": 3, "b": 4.0, "c": "d", "d": ["A", 1]}'

def test_dummy_encode():
    # arrange 
    dummy = DummyClass(2, 3.0, "4", DummyEnum.B)

    # act
    result = dummy.encode()

    # assert 
    assert result == {"a": 2, "b": 3.0, "c": "4", "d": ['B', 2]}

