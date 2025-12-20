from enum import Enum
from subprocess import *
from src.utilities.value_range import ValueRange
from src.reports.duplication_report import DuplicationReport
from src.tools.duplication_tool_interface import DuplicationToolInterface
import xml.etree.ElementTree as xml

# DOCUMENTATION PMD:
# PMD-CDP: https://pmd.github.io/pmd/pmd_userdocs_cpd.html

class PMD_CPD_XMLTag(Enum):
    DUPLICATION_TAG   = "{https://pmd-code.org/schema/cpd-report}duplication"
    FILE_TAG          = "{https://pmd-code.org/schema/cpd-report}file"
    CODE_FRAGMENT_TAG = "{https://pmd-code.org/schema/cpd-report}codefragment"

class PMD_CopyPasteDetector(DuplicationToolInterface): 

    # Languages supported by PMD-CPD
    # https://docs.pmd-code.org/latest/tag_languages.html
    _EXTENSIONS = {
        ".py": "python",
        ".c" : "cpp",
        ".cpp" : "cpp",
        ".h" : "cpp",
        ".hpp": "cpp",
        ".java": "java",
        ".js": "ecmascript",
        ".ts": "ts",
        ".html": "html",
        ".go" : "go",
        ".css" : "css", 
        ".php" : "php",
        ".xml" : "xml"
    }   
    
    def _read_report(self, xmlNode : xml.Element, dir : str) -> DuplicationReport:
        lines : int = int(xmlNode.attrib["lines"])
        file_list : list[DuplicationReport.File] = []
        fragment : str = ""

        for node in xmlNode:
            if node.tag == PMD_CPD_XMLTag.FILE_TAG.value:
                path      = str(node.get("path").removeprefix(dir))
                line      = int(node.get("line"))
                endline   = int(node.get("endline"))
                column    = int(node.get("column"))
                endcolumn = int(node.get("endcolumn"))

                file = DuplicationReport.File(path, ValueRange(line, endline), ValueRange(column, endcolumn))
                file_list.append(file)
                continue

            if node.tag == PMD_CPD_XMLTag.CODE_FRAGMENT_TAG.value:
                fragment = str(node.text)
                break
        
        report = DuplicationReport(lines, fragment)
        for file in file_list:
            report.add_file(file)
            continue

        return report

    def _read_xml(self, text : str, dir : str) -> list[DuplicationReport]:
        report_list = []
        root = xml.fromstring(text) 

        for node in root:
            if node.tag == PMD_CPD_XMLTag.DUPLICATION_TAG.value: 
                report : DuplicationReport = self._read_report(node, dir)
                report_list.append(report)
                continue
     
        return report_list
    
    def _format_dir(self, dir : str) -> str:
        if dir.endswith("/"):
            return dir
        else:
            return dir + "/"

    def _start_pmd(self, language_id : str, dir : str) -> str:
        MINIMUM_TOKENS = 20
        args = [
            "/pmd/pmd-bin-7.18.0/bin/pmd", "cpd", 
            "--minimum-tokens", str(MINIMUM_TOKENS), 
            "--language", language_id, 
            "--format", "xml", 
            "--dir", dir, 
        ]

        done_proc = run(args, capture_output=True, text=True)
        return done_proc.stdout

    def run(self, dir : str,  file_extensions : set[str]) -> list[DuplicationReport]: 
        dir = self._format_dir(dir)
        result_list = []
        
        for extension in file_extensions:
            # on saute si l'extension n'est pas supportée
            if extension not in PMD_CopyPasteDetector._EXTENSIONS:
                continue

            language_id = PMD_CopyPasteDetector._EXTENSIONS[extension]
            output = self._start_pmd(language_id, dir)
            report = self._read_xml(output, dir)
            result_list.extend(report)
            continue

        return result_list
