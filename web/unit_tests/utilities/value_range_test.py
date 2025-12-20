from src.utilities.value_range import ValueRange

def test_value_is_within():
    # arrange
    vr = ValueRange(0, 100)

    # act
    result = vr.is_value_within(40)
    
    # assert 
    assert result

def test_value_is_not_within():
    # arrange
    vr = ValueRange(0, 100)

    # act
    result = vr.is_value_within(-1)
    
    # assert 
    assert not result

def test_encode(): 
    # arrange
    vr = ValueRange(0, 100)

    # act
    result = vr.encode()

    # assert
    assert len(result) == 2
    assert "From" in result
    assert "To" in result
    assert result["From"] == 0
    assert result["To"] == 100