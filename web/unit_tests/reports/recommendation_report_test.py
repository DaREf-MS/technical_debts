from src.reports.recommendation_report import *
from src.reports.recommendation_generator import *

def test_summary_add_no_problem():
    # arrange
    summary = RecommendationReport.Summary("123.py")
    pair = Pair(ProblemEnum.NO_PROBLEM.value, RecommendationEnum.NO_RECOMMENDATION.value)

    # act
    summary.add(pair)

    # assert
    assert len(summary.problems) == 0
    assert len(summary.recommendations) == 0

def test_summary_add_problem():
    # arrange
    summary = RecommendationReport.Summary("123.py")
    pair1 = Pair(ProblemEnum.FILE_AVG_RISK_PROBLEM, RecommendationEnum.FILE_RISK_RECOMMENDATION)
    pair2 = Pair(ProblemEnum.FILE_FUNC_RISK_PROBLEM, RecommendationEnum.FILE_RISK_RECOMMENDATION)

    # act
    summary.add(pair1)
    summary.add(pair2)

    # assert
    assert len(summary.problems) == 2
    assert len(summary.recommendations) == 1  
            # only one recommendation because 
            # summary uses sets;


