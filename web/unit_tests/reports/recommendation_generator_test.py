from src.reports.recommendation_generator import *

func_report = [FunctionComplexityReport("abc.py", "func0()", 0, 10),
               FunctionComplexityReport("abc.py", "func1()", 0, 20),
               FunctionComplexityReport("def.py", "func2()", 0, 30),
               FunctionComplexityReport("def.py", "func3()", 0, 40)]

complexity = {"abc.py": FileComplexityReport("abc.py").load([func_report[0], func_report[1]]),
              "def.py": FileComplexityReport("def.py").load([func_report[2], func_report[3]])}

entity = {"abc.py": [EntityReport("abc.py", "todo", 1)],
          "def.py": [EntityReport("def.py", "todo", 1)], 
          "ghi.py": [EntityReport("ghi.py", "todo", 1)]}

def test__generate():
    # arrange
    problem = ProblemEnum.GLOBAL_DUPLICATION_PROBLEM
    expected = problem.value.replace("@1", str(1))
    recommendation = RecommendationEnum.GLOBAL_DUPLICATION_RECOMMENDATION
    generator = RecommendationGenerator()
    mapping = {"@1": 1}
    
    # act
    result_problem = generator._generate(problem, recommendation, mapping, True)
    result_no_problem = generator._generate(problem, recommendation, mapping, False)

    # assert
    assert result_problem.first == expected
    assert result_problem.second == recommendation.value
    assert result_no_problem.first == ProblemEnum.NO_PROBLEM.value
    assert result_no_problem.second == RecommendationEnum.NO_RECOMMENDATION.value
    
def test__global_risk():
    # arrange
    global func_report
    global complexity
    generator = RecommendationGenerator()
    
    # act 
    result = generator._global_risk(complexity)

    # assert
    assert result.first == ProblemEnum.GLOBAL_RISK_PROBLEM.value.replace("@1", RiskEnum.HIGH_RISK.name)
    assert result.second == RecommendationEnum.GLOBAL_RISK_RECOMMENDATION.value

def test__global_duplication():
    class LocalReportMock(DuplicationReport):
        def __init__(self):
            super().__init__(0, "")

        def get_file_nb(self):
            return 6
    
    # arrange
    duplication = {"abc.py": LocalReportMock(), "def.py": LocalReportMock()}
    generator = RecommendationGenerator()

    # act
    result = generator._global_duplication(duplication)

    # assert 
    assert result.first == ProblemEnum.GLOBAL_DUPLICATION_PROBLEM.value.replace("@1", str(12))
    assert result.second == RecommendationEnum.GLOBAL_DUPLICATION_RECOMMENDATION.value

def test__global_todofixme():
    # arrange
    global entity
    generator = RecommendationGenerator()

    # act 
    result = generator._global_todofixme(entity, 6)

    # assert
    assert result.first == ProblemEnum.GLOBAL_TODOFIXME_PROBLEM.value.replace("@1", str(6)).replace("@2", str(3))
    assert result.second == RecommendationEnum.GLOBAL_TODOFIXME_RECOMMENDATION.value

def test__file_avg_risk():
    # arrange
    global complexity
    generator = RecommendationGenerator()

    # act 
    result = generator._file_avg_risk(complexity["abc.py"])

    # assert
    assert result.first == ProblemEnum.FILE_AVG_RISK_PROBLEM.value.replace("@1", "abc.py").replace("@2", RiskEnum.MEDIUM_RISK.name)
    assert result.second == RecommendationEnum.FILE_RISK_RECOMMENDATION.value

def test__file_func_risk():
    # arrange
    global func_report
    generator = RecommendationGenerator()

    # act 
    result = generator._file_func_risk(func_report[2])

    # assert
    assert result.first == ProblemEnum.FILE_FUNC_RISK_PROBLEM.value.replace("@1", "def.py").replace("@2", "func2()").replace("@3", RiskEnum.HIGH_RISK.name)
    assert result.second == RecommendationEnum.FILE_RISK_RECOMMENDATION.value

def test__file_func_nb():
    # arrange
    generator = RecommendationGenerator()
    complexity = FileComplexityReport("abc.py")

    for i in range(0, 32):
        complexity.functions.append(FunctionComplexityReport())

    # act 
    result = generator._file_func_nb(complexity)

    # assert
    assert result.first == ProblemEnum.FILE_FUNC_NUMBER_PROBLEM.value.replace("@1", "abc.py").replace("@2", str(len(complexity.functions)))
    assert result.second == RecommendationEnum.FILE_FUNC_NUMBER_RECOMMENDATION.value