from src.reports.recommendation_generator import ProblemEnum
from src.utilities.json_encoder import JsonEncoder
from src.utilities.pair import Pair
from enum import Enum

class RecommendationReport(JsonEncoder.Interface):
    class Summary(JsonEncoder.Interface):
        subject : str
        problems : set[str]
        recommendations : set[str]
        
        def __init__(self, subject : str):
            self.subject = subject
            self.problems = set[str]()
            self.recommendations = set[str]()

        def add(self, problem_recomm : Pair[str, str]):
            if problem_recomm.first == ProblemEnum.NO_PROBLEM.value:
                return self

            self.problems.add(problem_recomm.first)
            self.recommendations.add(problem_recomm.second)
            return self
    
    _global : Summary
    _files : list[Summary]

    def __init__(self, global_summary : Summary, file_summaries : list[Summary]):
        self._global = global_summary
        self._files = file_summaries
        return
