from src.reports.function_complexity_report import FunctionComplexityReport
from src.utilities.selector import Selector
from src.utilities.json_encoder import JsonEncoder
from enum import Enum
import statistics

class RiskEnum(Enum):
    LOW_RISK = 0
    MEDIUM_RISK = 1
    HIGH_RISK = 2
    VERY_HIGH_RISK = 3

    def get_risk(complexity : float) -> Enum: 
        # Source: Murphy, James & Robinson III, John. (2007). Design of a Research Platform 
        #         for En Route Conflict Detection and Resolution. 10.2514/6.2007-7803. 
        # https://www.researchgate.net/figure/Cyclomatic-Complexity-Thresholds_tbl2_238659831

        if(complexity <= 10): return RiskEnum.LOW_RISK
        if(complexity <= 20): return RiskEnum.MEDIUM_RISK
        if(complexity <= 50): return RiskEnum.HIGH_RISK
        else:                 return RiskEnum.VERY_HIGH_RISK

class FileComplexityReport(JsonEncoder.Interface):
    complexity : float
    filename : str
    functions : list[FunctionComplexityReport] 

    def __init__(self, filename : str):
        self.functions = []
        self.filename = filename
        self.complexity = 0.0
        return
    
    def update_complexity(self):
        selector = Selector(self.functions, lambda func: float(func.cyclomatic_complexity))
        complexity : float = statistics.mean(selector)
        self.complexity = complexity

    def load(self, functions : list[FunctionComplexityReport]):
        self.functions.extend(functions)
        self.update_complexity()
        return self
