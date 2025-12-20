from src.controllers.duplication_controller import (DuplicationController, 
                                                    DuplicationReport, 
                                                    DuplicationToolInterface,
                                                    CodeDuplicationService,
                                                    File)
# --------------- mocks ---------------

class LocalToolMock(DuplicationToolInterface):
    called = False
    params_valid = True

    def setup():
        LocalToolMock.called = False
        LocalToolMock.params_valid = True

    def run(self, dir, file_extensions):
        LocalToolMock.called = True
        LocalToolMock.params_valid &= dir == "/dir" and file_extensions == {".py"}
        return [DuplicationReport(1, "hello")]
    
class LocalServiceMock(CodeDuplicationService):
    called = False
    params_valid = True

    def setup():
        LocalServiceMock.called = False
        LocalServiceMock.params_valid = True

    def __init__(self):
        super().__init__(None)
        return
    
    def insert_from_report(self, report_list, file_list):
        LocalServiceMock.called = True
        LocalServiceMock.params_valid &= len(report_list) == 1
        LocalServiceMock.params_valid &= report_list[0].get_fragment() == "hello"
        LocalServiceMock.params_valid &= len(file_list) == 2
        LocalServiceMock.params_valid &= file_list[0].name == "123.py"
        return
    
    def get_reports_for_many_files(self, file_list):
        LocalServiceMock.called = True
        LocalServiceMock.params_valid &= len(file_list) == 2
        LocalServiceMock.params_valid &= file_list[0].name == "123.py"
        return [DuplicationReport(1, "hello")]

class LocalControllerMock(DuplicationController):
    def _load_service(self):
        self._service = LocalServiceMock()
        return
    
    def _load_tools(self):
        self._tools["test"] = LocalToolMock()
        return 

# --------------- unit tests ---------------

def test_singleton__first_created(): 
    # arrange
    DuplicationController._singleton = None

    # act
    controller : DuplicationController = DuplicationController.singleton()

    # assert
    assert controller != None
    assert controller._service != None
    assert len(controller._tools) >= 1
    assert DuplicationController._singleton != None
    return

def test_singleton__already_created():
    # arrange
    DuplicationController._singleton = None
    created_controller = DuplicationController.singleton()

    #act
    controller : DuplicationController = DuplicationController.singleton()

    # assert
    assert controller == created_controller
    return

def test_find_duplications():
    # arrange
    LocalToolMock.setup()
    LocalServiceMock.setup()

    controller = LocalControllerMock()
    file_list = [ File(id="a", name="123.py", commit_id="."),
                  File(id="b", name="456.py", commit_id=".") ]

    # act
    controller.find_duplications("test", "/dir", file_list)
    
    # assert 
    assert LocalToolMock.called and LocalToolMock.params_valid
    assert LocalServiceMock.called and LocalServiceMock.params_valid
    return

def test_find_duplications__tool_not_found():
    # arrange
    LocalToolMock.setup()
    LocalServiceMock.setup()

    controller = LocalControllerMock()
    file_list = []

    # act
    try:
        controller.find_duplications("aaaaaaaaaa", "/dir", file_list)
    
    # assert 
        assert False
    except:
        assert True
    return

def test_get_report_dict():
    # arrange
    LocalToolMock.setup()
    LocalServiceMock.setup()

    controller = LocalControllerMock()
    file_list = [ File(id="a", name="123.py", commit_id="."),
                  File(id="b", name="456.py", commit_id=".") ]
    
    # act
    result = controller.get_report_dict(file_list)

    # assert
    assert LocalServiceMock.called and LocalServiceMock.params_valid
    assert len(result) == 1
    assert result[0]._fragment == "hello"
    return

def test_get_tool_name_set():
    # arrange
    LocalToolMock.setup()
    LocalServiceMock.setup()
    controller = LocalControllerMock()

    # act
    tools = controller.get_tool_name_set()

    # assert
    assert tools == {"test"}
