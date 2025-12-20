from src.reports.file_complexity_report import FileComplexityReport, RiskEnum
from src.reports.function_complexity_report import FunctionComplexityReport
from src.reports.duplication_report import DuplicationReport
from src.reports.entity_report import EntityReport
from src.utilities.selector import Selector
from src.utilities.pair import Pair
from enum import Enum
import statistics

class ProblemEnum(Enum):
    NO_PROBLEM = "No problems."
    GLOBAL_RISK_PROBLEM = "50% of files in this commit have an average complexity ranked at or above @1."
    GLOBAL_DUPLICATION_PROBLEM = "@1 instances of code duplication have been detected in this commit. Details in 'Duplication' section."
    GLOBAL_TODOFIXME_PROBLEM = "For a total of @1 files, @2 files contained at least one 'todo' or 'fixme'."
    FILE_AVG_RISK_PROBLEM = "File @1 has an average complexity ranked at or above @2."
    FILE_FUNC_RISK_PROBLEM = "File @1 has complexity of function @2 ranked at or above @3."
    FILE_FUNC_NUMBER_PROBLEM = "File @1 has a total of @2 functions."

class RecommendationEnum(Enum):
    NO_RECOMMENDATION = ""
    GLOBAL_RISK_RECOMMENDATION = "Simplify logic and reduce complexity by limiting the number of independent paths in your functions. " \
                                 "Break appart large complex functions into smaller, simpler and testable functions."
    GLOBAL_DUPLICATION_RECOMMENDATION = "Move duplicated code into new coherent and cohesive functions and modules for reusability, " \
                                        "readability, maintainability and testability."
    GLOBAL_TODOFIXME_RECOMMENDATION = "Dedicate more ressources to fix bugs and implement missing features. Consider writing tests."
    FILE_RISK_RECOMMENDATION = "Simplify logic and reduce complexity by limiting the number of independent paths. " \
                               "Break appart large and complex logic blocks into smaller, loosely coupled and testable functions."
    FILE_FUNC_NUMBER_RECOMMENDATION = "Decrease the number of functions either by redesigning your architecture or creating a new module. " \
                                      "A large number of functions can be signs of high coupling and low cohesion, and usually decreases " \
                                      "readability and maintainability."

class RecommendationGenerator:
    def _generate(self, 
                  problem : ProblemEnum, 
                  recommendation : RecommendationEnum, 
                  mapping : dict[str, object],
                  is_problem : bool) -> Pair[str, str]:
        if is_problem == False:
            return Pair(ProblemEnum.NO_PROBLEM.value, RecommendationEnum.NO_RECOMMENDATION.value)

        _problem_value = str(problem.value)
        _recommendation_value = str(recommendation.value)

        for key in mapping:
            _problem_value = _problem_value.replace(key, str(mapping[key]))
            continue

        return Pair(_problem_value, _recommendation_value)
    
    def _global_risk(self, complexities : dict[str, FileComplexityReport]) -> Pair[str, str]:
        selector = Selector(complexities, lambda filename: complexities[filename].complexity)
        median : float = statistics.median(selector)
        risk : RiskEnum = RiskEnum.get_risk(median)
        mapping = {"@1" : risk.name}

        return self._generate(ProblemEnum.GLOBAL_RISK_PROBLEM, 
                              RecommendationEnum.GLOBAL_RISK_RECOMMENDATION, 
                              mapping,
                              risk.value >= RiskEnum.MEDIUM_RISK.value)

    def _global_duplication(self, duplications : dict[str, DuplicationReport]) -> Pair[str, str]:
        selector = Selector(duplications, lambda fragment_id: duplications[fragment_id].get_file_nb())
        duplication_count = sum(selector)
        mapping = {"@1": str(duplication_count)}
        
        MINIMUM_DUPLICATION_COUNT = 5
        return self._generate(ProblemEnum.GLOBAL_DUPLICATION_PROBLEM,
                              RecommendationEnum.GLOBAL_DUPLICATION_RECOMMENDATION,
                              mapping,
                              duplication_count >= MINIMUM_DUPLICATION_COUNT)

    def _global_todofixme(self, entities : dict[str, list[EntityReport]], total_file_nb : int) -> Pair[str, str]:
        bugged_file_count = len(entities.keys())
        bugged_normal_ratio = float(bugged_file_count) / float(total_file_nb)
        mapping = {"@1": str(total_file_nb), "@2": str(bugged_file_count)}

        MINIMUM_RATIO = 0.07 # considered a problem if at least 7% of all files in commit have at least one bug.
        return self._generate(ProblemEnum.GLOBAL_TODOFIXME_PROBLEM,
                              RecommendationEnum.GLOBAL_TODOFIXME_RECOMMENDATION,
                              mapping,
                              bugged_normal_ratio >= MINIMUM_RATIO)

    def _file_avg_risk(self, complexity : FileComplexityReport) -> Pair[str, str]:
        risk = RiskEnum.get_risk(complexity.complexity)
        mapping = {"@1": complexity.filename, "@2": risk.name}

        return self._generate(ProblemEnum.FILE_AVG_RISK_PROBLEM,
                              RecommendationEnum.FILE_RISK_RECOMMENDATION, 
                              mapping,
                              risk.value >= RiskEnum.MEDIUM_RISK.value)
        
    def _file_func_risk(self, complexity : FunctionComplexityReport) -> Pair[str, str]:
        risk : RiskEnum = RiskEnum.get_risk(complexity.cyclomatic_complexity)
        mapping = {"@1": complexity.file, "@2": complexity.function, "@3": risk.name}

        return self._generate(ProblemEnum.FILE_FUNC_RISK_PROBLEM, 
                              RecommendationEnum.FILE_RISK_RECOMMENDATION, 
                              mapping,
                              risk.value >= RiskEnum.MEDIUM_RISK.value)        

    def _file_func_nb(self, complexity : FileComplexityReport) -> Pair[str, str]:
        func_nb = len(complexity.functions)
        mapping = {"@1": complexity.filename, "@2": str(func_nb)}

        MINIMUM_FUNC_NUMBER = 30
        return self._generate(ProblemEnum.FILE_FUNC_NUMBER_PROBLEM, 
                              RecommendationEnum.FILE_FUNC_NUMBER_RECOMMENDATION, 
                              mapping,
                              func_nb >= MINIMUM_FUNC_NUMBER)
