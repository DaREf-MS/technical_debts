from src.utilities.pair import Pair

def test_to_tuple():
    # arrange
    pair = Pair[int, str](123, "soleil")

    # act
    _tuple = pair.as_tuple()

    # assert 
    assert _tuple[0] == 123
    assert _tuple[1] == "soleil"

def test_encode():
    # arrange
    pair = Pair[int, str](123, "soleil")

    # act
    obj = pair.encode()

    # assert
    assert obj[0] == 123
    assert obj[1] == "soleil"