from src.reports.recommendation_generator import RecommendationGenerator
from src.services.recommendation_service import RecommendationService
from src.services.compatibility_service import CompatibilityService
from src.reports.file_complexity_report import FileComplexityReport
from src.reports.recommendation_report import RecommendationReport
from src.reports.duplication_report import DuplicationReport
from src.reports.entity_report import EntityReport
from src.models.model import File

class RecommendationController:
    _singleton = None
    _compatibility : CompatibilityService
    _recommendation : RecommendationService

    def singleton(): 
        if RecommendationController._singleton == None:
            controller = RecommendationController()
            RecommendationController._singleton = controller

        return RecommendationController._singleton
    
    def __init__(self):
        self._compatibility = None
        self._recommendation = None
        self._load_service()
        return

    def _load_service(self):
        generator = RecommendationGenerator()
        self._compatibility = CompatibilityService()
        self._recommendation = RecommendationService(generator)
        return

    def get_recommendations(self, 
                            file_list    : list[File],
                            complexities : list[list[dict[str, object]]], 
                            entities     : list[dict[str, object]], 
                            duplication  : dict[str, DuplicationReport]) -> RecommendationReport:
        _complexities   = self._compatibility.convert_file_complexity_objects(complexities)
        _entities       = self._compatibility.convert_entity_objects(entities)
        recommendations = self._recommendation.get_recommendations(file_list, _complexities, _entities, duplication)
        return recommendations
    