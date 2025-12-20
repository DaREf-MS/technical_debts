from src.tools.duplication_tool_interface import DuplicationToolInterface

def test_run__expecting_exception():
    # arrange
    tool = DuplicationToolInterface()

    # act
    result = tool.run("", set())

    # assert
    assert result == []