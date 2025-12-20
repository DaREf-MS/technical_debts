from src.controllers.recommendation_controller import *

class LocalRecommendationServiceMock(RecommendationService):
    called = False
    params_valid = True

    def setup():
        LocalRecommendationServiceMock.called = False
        LocalRecommendationServiceMock.params_valid = True

    def __init__(self):
        super().__init__(None)


    def get_recommendations(self, file_list, complexity, entity, duplication):
        LocalRecommendationServiceMock.called = True
        LocalRecommendationServiceMock.params_valid &= file_list[0].name == "abc.py"
        LocalRecommendationServiceMock.params_valid &= complexity["abc.py"].filename == "abc.py"
        LocalRecommendationServiceMock.params_valid &= entity["abc.py"][0].entity_name == "todo"
        LocalRecommendationServiceMock.params_valid &= duplication["abc.py"]._fragment == "test"
        return RecommendationReport(RecommendationReport.Summary("All"), [])
    
class LocalCompatibilityServiceMock(CompatibilityService):
    called = 0
    params_valid = False

    def setup():
        LocalCompatibilityServiceMock.called = 0
        LocalCompatibilityServiceMock.params_valid = True

    def __init__(self):
        super().__init__()

    def convert_file_complexity_objects(self, file_list):
        LocalCompatibilityServiceMock.called += 1
        LocalCompatibilityServiceMock.params_valid &= file_list == [[{"file":"abc.py", 
                                                                      "function":"test()", 
                                                                      "start_line":1, 
                                                                      "cyclomatic_complexity":10}]]
        return {"abc.py" : FileComplexityReport("abc.py")}
    
    def convert_entity_objects(self, entity_list):
        LocalCompatibilityServiceMock.called += 1
        LocalCompatibilityServiceMock.params_valid &= entity_list == [{"file_name":"abc.py", 
                                                                        "entity_name":"todo", 
                                                                        "line_position":1}]
        return {"abc.py": [EntityReport("abc.py", "todo", 1)]}
    
class LocalControllerMock(RecommendationController):
    def _load_service(self):
        self._compatibility = LocalCompatibilityServiceMock()
        self._recommendation = LocalRecommendationServiceMock()

# --------------- unit tests ---------------

def test_singleton__first_created():
    # arrange
    RecommendationController._singleton = None

    # act
    controller : RecommendationController = RecommendationController.singleton()

    # assert
    assert controller != None
    assert controller._compatibility != None
    assert controller._recommendation != None
    assert RecommendationController._singleton == controller

def test_singleton__already_created(): 
    # arrange
    RecommendationController._singleton = None
    created_controller : RecommendationController = RecommendationController.singleton()

    # act
    controller : RecommendationController = RecommendationController.singleton()

    # assert
    assert created_controller == controller

def test_get_recommendations():
    # arrange
    mock = LocalControllerMock()
    file_list = [File(id=".", name="abc.py", commit_id=".")]
    complexities = [[{"file":"abc.py", 
                      "function":"test()", 
                      "start_line":1, 
                      "cyclomatic_complexity":10}]]
    entities = [{"file_name":"abc.py", 
                  "entity_name":"todo", 
                  "line_position":1}]
    duplications =  {"abc.py": DuplicationReport(1, "test")}

    LocalRecommendationServiceMock.setup()
    LocalCompatibilityServiceMock.setup()
    
    # act
    result = mock.get_recommendations(file_list, complexities, entities, duplications)

    # assert
    assert LocalRecommendationServiceMock.called and LocalRecommendationServiceMock.params_valid
    assert LocalCompatibilityServiceMock.called == 2 and LocalCompatibilityServiceMock.params_valid
    assert result._global.subject == "All"