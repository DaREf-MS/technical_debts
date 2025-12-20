from src.reports.function_complexity_report import FunctionComplexityReport
from src.reports.file_complexity_report import FileComplexityReport
from src.reports.entity_report import EntityReport

class CompatibilityService: 
    """
    Assembles data structures containing file complexities, function complexities and identifiable entities (todo-fixme) 
    into type-enforced, workable, class instances. This is intended to provide compatibility with the recommendation service.
    """
    def convert_func_complexity_objects(self, func_list : list[dict[str, object]]) -> dict[str, list[FunctionComplexityReport]]:
        assert type(func_list) == list

        result = dict[str, list[FunctionComplexityReport]]()
        for obj in func_list:
            report = FunctionComplexityReport().load(obj)

            if report.file not in result:
                result[report.file] = list[FunctionComplexityReport]()
            
            result[report.file].append(report)
            continue

        return result

    def convert_file_complexity_objects(self, file_list : list[list[dict[str, object]]]) -> dict[str, FileComplexityReport]:
        assert type(file_list) == list

        result = dict[str, FileComplexityReport]()
        for obj_list in file_list:
            functions = self.convert_func_complexity_objects(obj_list)

            for key in functions:
                if key in result:
                    result[key].load(functions[key])
                else: 
                    result[key] = FileComplexityReport(key).load(functions[key])
                continue
            continue
        return result
    
    def convert_entity_objects(self, entity_list : list[dict[str, object]]) -> dict[str, list[EntityReport]]:
        assert type(entity_list) == list

        report_dict = dict[str, list[EntityReport]]()
        for obj in entity_list:
            report = EntityReport().load(obj)

            if report.file_name not in report_dict:
                report_dict[report.file_name] = list[EntityReport]()
            
            report_dict[report.file_name].append(report)
            continue

        return report_dict
    