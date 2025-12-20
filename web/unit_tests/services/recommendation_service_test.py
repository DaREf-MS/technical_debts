from src.reports.function_complexity_report import FunctionComplexityReport
from src.services.recommendation_service import RecommendationService
from src.reports.file_complexity_report import FileComplexityReport
from src.reports.duplication_report import DuplicationReport
from src.reports.recommendation_generator import *
from src.reports.recommendation_report import *
from src.models.model import *

class LocalGeneratorMock(RecommendationGenerator):
    risk = Pair(ProblemEnum.GLOBAL_RISK_PROBLEM.value.replace("@1", RiskEnum.HIGH_RISK.name),
                RecommendationEnum.GLOBAL_RISK_RECOMMENDATION.value)
    duplication = Pair(ProblemEnum.GLOBAL_DUPLICATION_PROBLEM.value.replace("@1", str(12)),
                       RecommendationEnum.GLOBAL_DUPLICATION_RECOMMENDATION.value)
    bug = Pair(ProblemEnum.GLOBAL_TODOFIXME_PROBLEM.value.replace("@1", str(6)).replace("@2", str(3)),
               RecommendationEnum.GLOBAL_TODOFIXME_RECOMMENDATION.value)
    file_risk = Pair(ProblemEnum.FILE_AVG_RISK_PROBLEM.value.replace("@1", "abc.py").replace("@2", RiskEnum.MEDIUM_RISK.name),
                     RecommendationEnum.FILE_RISK_RECOMMENDATION.value)
    func_risk = Pair(ProblemEnum.FILE_FUNC_RISK_PROBLEM.value.replace("@1", "def.py").replace("@2", "func2()").replace("@3", RiskEnum.HIGH_RISK.name), 
                   RecommendationEnum.FILE_RISK_RECOMMENDATION.value)
    func_nb = Pair(ProblemEnum.FILE_FUNC_NUMBER_PROBLEM.value.replace("@1", "abc.py").replace("@2", str(32)),
                     RecommendationEnum.FILE_FUNC_NUMBER_RECOMMENDATION.value)
    
    def _global_risk(self, complexities):
        return LocalGeneratorMock.risk
    
    def _global_duplication(self, duplications):
        return LocalGeneratorMock.duplication

    def _global_todofixme(self, entities, total_file_nb):
        return LocalGeneratorMock.bug
    
    def _file_avg_risk(self, complexity):
        return LocalGeneratorMock.file_risk
    
    def _file_func_risk(self, complexity):
        return LocalGeneratorMock.func_risk
    
    def _file_func_nb(self, complexity):
        return LocalGeneratorMock.func_nb
    
def test_get_global_summary():
    # arrange
    mock = LocalGeneratorMock()
    service = RecommendationService(mock)

    # act 
    result = service.get_global_summary(1, {}, {}, {})

    # assert
    assert result.subject == "All"
    assert LocalGeneratorMock.risk.first in result.problems
    assert LocalGeneratorMock.duplication.first in result.problems
    assert LocalGeneratorMock.bug.first in result.problems

def test_get_file_complexity_summary():
    class LocalServiceMock(RecommendationService):
        params_valid = True

        def __init__(self, generator):
            super().__init__(generator)

        def get_file_complexity_summary(self, summary, complexity):
            LocalServiceMock.params_valid &= type(summary) == RecommendationReport.Summary
            LocalServiceMock.params_valid &= type(complexity) == FileComplexityReport
            return super().get_file_complexity_summary(summary, complexity)

    # arrange
    mock = LocalGeneratorMock()
    service = RecommendationService(mock)
    summary = RecommendationReport.Summary("file.py")
    complexity = FileComplexityReport("file.py").load([FunctionComplexityReport()])

    # act 
    result = service.get_file_complexity_summary(summary, complexity)

    # assert
    assert LocalServiceMock.params_valid
    assert LocalGeneratorMock.file_risk.first in result.problems
    assert LocalGeneratorMock.file_risk.second in result.recommendations
    assert LocalGeneratorMock.func_risk.first in result.problems
    assert LocalGeneratorMock.func_risk.second in result.recommendations
    assert LocalGeneratorMock.func_nb.first in result.problems
    assert LocalGeneratorMock.func_nb.second in result.recommendations

def test_get_file_summary():
    class LocalServiceMock(RecommendationService):
        params_valid = True

        def __init__(self):
            super().__init__(None)

        def get_file_complexity_summary(self, summary, complexity):
            LocalServiceMock.params_valid &= type(complexity) == FileComplexityReport
            summary.add(LocalGeneratorMock.file_risk)
            return summary
    
    # arrange
    mock = LocalServiceMock()

    # act 
    result = mock.get_file_summary("abc.py", {"abc.py": FileComplexityReport("abc.py")}, {}, {})

    # assert
    assert LocalServiceMock.params_valid
    assert result.subject == "abc.py"
    assert LocalGeneratorMock.file_risk.first in result.problems
    assert LocalGeneratorMock.file_risk.second in result.recommendations

def test_get_recommendations():
    class LocalServiceMock(RecommendationService):
        params_valid = True

        def __init__(self):
            super().__init__(None)

        def get_global_summary(self, total_file_nb, complexity, entity, duplication):
            LocalServiceMock.params_valid &= total_file_nb == 1 and complexity == {} and entity == {} and duplication == {}
            return RecommendationReport.Summary("All").add(LocalGeneratorMock.duplication)
        
        def get_file_summary(self, filename, complexity, entity, duplication):
            LocalServiceMock.params_valid &= filename == "abc.py" and complexity == {} and entity == {} and duplication == {}
            return RecommendationReport.Summary("abc.py").add(LocalGeneratorMock.func_nb)
        
    # arrange
    mock = LocalServiceMock()

    # act 
    result = mock.get_recommendations([File(id=".",name="abc.py",commit_id=".")], {}, {}, {})

    # assert
    assert len(result._files) == 1
    assert LocalGeneratorMock.func_nb.first in result._files[0].problems
    assert LocalGeneratorMock.func_nb.second in result._files[0].recommendations
    assert result._global.subject == "All"
    assert LocalGeneratorMock.duplication.first in result._global.problems
    assert LocalGeneratorMock.duplication.second in result._global.recommendations
