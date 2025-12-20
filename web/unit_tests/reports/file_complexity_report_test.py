from src.reports.file_complexity_report import *

def test__risk_enum__get_risk():
    # arrange

    # act
    results = [RiskEnum.get_risk(1),
               RiskEnum.get_risk(13),
               RiskEnum.get_risk(23),
               RiskEnum.get_risk(60)]

    # assert
    assert results == [RiskEnum.LOW_RISK, 
                       RiskEnum.MEDIUM_RISK, 
                       RiskEnum.HIGH_RISK, 
                       RiskEnum.VERY_HIGH_RISK]
    
def test__file_complexity_report__update_complexity():
    # arrange
    report = FileComplexityReport("123.py")
    report.functions = [FunctionComplexityReport("123.py", "func0()", 0, 1),
                        FunctionComplexityReport("123.py", "func1()", 0, 2),
                        FunctionComplexityReport("123.py", "func2()", 0, 3)]
    
    # act
    report.update_complexity()

    # assert
    assert report.complexity == (1.0 + 2.0 + 3.0) / 3.0
    
