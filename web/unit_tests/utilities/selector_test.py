from src.utilities.selector import Selector

def test_selector():
    # arrange
    collection = {"a": [1, 2, 3], "b": [4, 5, 6]}
    expected = [1, 4]
    result = [False, False]
    selector = Selector(collection, lambda key: collection[key][0])
    i = 0

    # act
    for v in selector:
        result[i] = v == expected[i]
        i += 1
        continue

    # assert
    assert result[0] and result[1]
    return