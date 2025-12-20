import json
from enum import Enum

class JsonEncoder: 
    class Interface:
        def encode(self): 
            return JsonEncoder.breakdown(self.__dict__) 
    
    def _raise_unsupported_type_exception(type_name : str):
        msg = type_name + " is not a supported type. Either use a dict, tuple, set, list, or extend the JsonEncoder.Interface class."
        raise Exception()

    def _raise_invalid_dict_key_exception(type_name : str):
        msg = "For JSON encoding, only 'str' and 'int' are valid 'dict' key types.\n Recieved: " + type_name
        raise Exception(msg)

    def _enum_to_raw(_enum: Enum):
        return JsonEncoder._tuple_to_raw((_enum.name, _enum.value))

    def _dict_to_raw(_dict: dict):
        for k in _dict:
            if not (isinstance(k, str) or isinstance(k, int)):
                JsonEncoder._raise_invalid_dict_key_exception(type(k).__name__)   
            
            _dict[k] = JsonEncoder._object_to_raw(_dict[k])
        return _dict

    def _list_to_raw(_list: list[object]):
        i = 0
        m = len(_list)
        while i < m:
            _list[i] = JsonEncoder._object_to_raw(_list[i])
            i += 1
        return _list
    
    def _tuple_to_raw(_tuple: tuple[object]):
        temp_list = []
        for v in _tuple:
            temp_list.append(JsonEncoder._object_to_raw(v))
        return temp_list
    
    def _set_to_raw(_set: set[object]): 
        temp_list = []
        for v in _set:
            temp_list.append(JsonEncoder._object_to_raw(v))
        return temp_list

    def _primitive_to_raw(primitive : object):
        return primitive

    def _object_to_raw(_obj : object): 
        type_dict = {
            dict.__name__: JsonEncoder._dict_to_raw,
            list.__name__: JsonEncoder._list_to_raw,
            tuple.__name__: JsonEncoder._tuple_to_raw,
            set.__name__: JsonEncoder._set_to_raw,
            int.__name__: JsonEncoder._primitive_to_raw,
            float.__name__: JsonEncoder._primitive_to_raw,
            bool.__name__: JsonEncoder._primitive_to_raw,
            str.__name__: JsonEncoder._primitive_to_raw,
            type(None).__name__: JsonEncoder._primitive_to_raw
        }

        typename = type(_obj).__name__
        if typename in type_dict:
            return type_dict[typename](_obj)

        if isinstance(_obj, JsonEncoder.Interface):
            return _obj.encode()
        
        if isinstance(_obj, Enum):
            return JsonEncoder._enum_to_raw(_obj)

        JsonEncoder._raise_unsupported_type_exception(type(_obj).__name__)

    def breakdown(obj):
        """
        breaks appart complex python objects into 
        simpler objects that can be dumped as json
        with `json.dumps()`.
        """
        return JsonEncoder._object_to_raw(obj)

    def dump(obj):
        """
        Converts a python object into a JSON string.
        """
        raw = JsonEncoder.breakdown(obj)
        return json.dumps(raw)
