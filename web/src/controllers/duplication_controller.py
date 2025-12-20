from src.models.model import File
from src.tools.pmd_copy_paste_detector import PMD_CopyPasteDetector
from src.tools.duplication_tool_interface import DuplicationToolInterface
from src.database.code_duplication_db_facade import CodeDuplicationDatabaseFacade
from src.services.code_duplication_service import CodeDuplicationService
from src.reports.duplication_report import DuplicationReport
from src.utilities.extensions import Extensions

class DuplicationController: 
    _singleton = None
    _service : CodeDuplicationService
    _tools : dict[str, DuplicationToolInterface]

    def singleton():
        if DuplicationController._singleton == None:
            controller = DuplicationController()
            DuplicationController._singleton = controller

        return DuplicationController._singleton

    def __init__(self): 
        self._service = None
        self._tools = dict()
        self._load_tools()
        self._load_service()
        return
    
    def _load_service(self):
        facade = CodeDuplicationDatabaseFacade()
        self._service = CodeDuplicationService(facade)
        return
        
    def _load_tools(self):
        # instancier les outils ici
        pmd_cpd = PMD_CopyPasteDetector()

        # insérer les outils ici
        self._tools["pmd_cpd"] = pmd_cpd
        return 

    def find_duplications(self, tool : str, dir : str, files : list[File]):

        if len(files) > 0:
            #print(type(files[0]))
            assert isinstance(files[0], File)

        # --temporaire-- 
        # pour trouver les langages utilisés dans le projet 
        file_extensions = Extensions.get_extension_set(files)

        if tool not in self._tools:
            raise Exception(tool + " is not a valid duplication tool.")
        
        duplication_tool = self._tools[tool]
        report_list = duplication_tool.run(dir, file_extensions)

        self._service.insert_from_report(report_list, files)
        return
    
    def get_report_dict(self, files : list[File]) -> dict[str, DuplicationReport]:
        return self._service.get_reports_for_many_files(files)
    
    def get_tool_name_set(self) -> set[str]:
        return set(self._tools.keys())
