from src.database.code_duplication_db_facade import *
from src.reports.duplication_report import DuplicationReport
from src.models.model import File

class CodeDuplicationService: 
    _facade : CodeDuplicationDatabaseFacade

    def __init__(self, facade : CodeDuplicationDatabaseFacade): 
        self._facade = facade

    def insert(self, fragments : list[CodeFragment], duplications : list[Duplication]):
        self._facade.insert_many_fragments(fragments)
        self._facade.insert_many_duplications(duplications)

    def get_fragment_by_id(self, id : str) -> CodeFragment:
        return self._facade.get_duplication_by_id(id)

    def get_reports_for_many_files(self, file_list : list[File]) -> dict[str, DuplicationReport]:
        file_id_dict = dict[str, File]()
        for f in file_list: 
            file_id_dict[f.id] = f

        fragment_list = self._facade.get_fragments_for_many_file(file_list)
        report_dict = dict[str, DuplicationReport]()

        for element in fragment_list:
            fragment : CodeFragment = element[0]
            duplication : Duplication = element[1]
            file = file_id_dict[duplication.file_id]

            if fragment.id not in report_dict:
                report = DuplicationReport(fragment.line_count, fragment.text)
                report_dict[fragment.id] = report

            report_element = DuplicationReport.File(file.name, duplication.lines(), duplication.columns())
            report = report_dict[fragment.id]
            report.add_file(report_element)
        return report_dict
    
    def insert_from_report(self, report_list : list[DuplicationReport], file_list : list[File]):  
        filename_dict : dict[str, File] = {}
        for file in file_list: 
            filename_dict[file.name] = file

        duplication_list : list[Duplication] = []
        fragments_list : list[CodeFragment] = []

        for report in report_list:
            fragment = CodeFragment(report.get_fragment(), report.get_lines())
            fragments_list.append(fragment)
            lines = report.get_lines()
            
            for element in report:
                if element.filename not in filename_dict:
                    raise Exception("filename '" + element.filename + "' in duplication report does not exists in database.")
        
                file : File = filename_dict[element.filename]
                duplication = Duplication(fragment.id, file.id, lines, element.lines, element.columns)
                duplication_list.append(duplication)

        self.insert(fragments_list, duplication_list)
        return