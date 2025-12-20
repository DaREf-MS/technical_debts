from src.tools.pmd_copy_paste_detector import PMD_CopyPasteDetector
from src.utilities.json_encoder import JsonEncoder
from src.reports.duplication_report import DuplicationReport
from src.utilities.value_range import ValueRange
import re

#def test_run_python(): 
#    # arrange
#    wrapper = PMD_CopyPasteDetector(20, [PMD_CopyPasteDetector.Language.PYTHON], "/app/unit_tests/tools/pmd_cpd_test_directory")
#    expected_output = ""
#
#    with open("/app/unit_tests/tools/pmd_cpd_test_directory/pmd_cpd_python_output.xml") as f:
#        expected_output = f.read()
#    expected_output = re.sub('timestamp=".+"', 'timestamp=""', expected_output) # We remove the timestamps, otherwise the test would always fail
#    
#    # act
#    result = wrapper.run()
#    result[0] = re.sub('timestamp=".+"', 'timestamp=""', result[0]) # We remove the timestamps, otherwise the test would always fail
#
#    # assert
#    assert result[0] == expected_output

def test_run():
    # assert 
    class LocalToolMock(PMD_CopyPasteDetector): 
        start_pmd_called = 0
        read_xml_called = 0
        params_valid = True

        def _format_dir(self, dir):
            LocalToolMock.params_valid &= dir == "/app/unit_tests/tools"
            return "/app/unit_tests/tools/"

        def _start_pmd(self, language_id, dir):
            LocalToolMock.start_pmd_called += 1
            LocalToolMock.params_valid &= language_id != ".invalid_extension"
            LocalToolMock.params_valid &= dir == "/app/unit_tests/tools/"
            return "<xml></xml>"
        
        def _read_xml(self, text, dir):
            LocalToolMock.read_xml_called += 1
            LocalToolMock.params_valid &= text == "<xml></xml>"
            LocalToolMock.params_valid &= dir == "/app/unit_tests/tools/"
            report = DuplicationReport(3, "hello world")
            report.add_file(DuplicationReport.File("test.py", ValueRange(0, 1), ValueRange(0, 1)))
            return [ report ]
        
    mock = LocalToolMock()

    # act
    result = mock.run("/app/unit_tests/tools", {".py", ".invalid_extension"})

    # assert 
    assert result[0]._files[0].filename == "test.py"
    assert result[0]._files[0].lines.From == 0
    assert result[0]._files[0].lines.To == 1
    assert result[0]._files[0].columns.From == 0
    assert result[0]._files[0].columns.To == 1
    return

def test_run_no_extensions():
    # arrange
    tool = PMD_CopyPasteDetector()

    # act
    result = tool.run("folder", {})

    # assert
    assert result == []

def test__start_pmd():
    # arrange
    class LocalToolMock(PMD_CopyPasteDetector):
        xml_valid = False
        called = False

        def _read_xml(self, text, dir):
            print(text)
            LocalToolMock.called = True
            xml_path = "/app/unit_tests/tools/pmd_cpd_test_directory/pmd_cpd_python_output.xml"
            io = open(xml_path)
            test_xml = io.read()
            io.close()
            # We remove the timestamps, otherwise the test would always fail
            text = re.sub('timestamp=".+"', 'timestamp=""', text)
            LocalToolMock.xml_valid = text == test_xml
            print(test_xml)
            return []

    
    wrapper = LocalToolMock()
    # We remove the timestamps, otherwise the test would always fail

    # act
    result = wrapper.run("/app/unit_tests/tools/pmd_cpd_test_directory", [".py"])
    
    # assert
    assert LocalToolMock.called == True
    assert LocalToolMock.xml_valid and result == []
    return

def test__read_xml():
    # arrange
    tool = PMD_CopyPasteDetector()
    expected_fragment = '    numbers = [1, 2, 3]\n    total = 0\n    for n in numbers:\n        total += n\n    return total\n\n\ndef duplicate_three():\n'
    xml_path = "/app/unit_tests/tools/pmd_cpd_test_directory/pmd_cpd_python_output.xml"
    repo_path = "/app/unit_tests/tools/"
    io = open(xml_path)
    test_xml = io.read()
    io.close()

    # act 
    report_list = tool._read_xml(test_xml, repo_path)

    # assert
    assert len(report_list) == 2
    assert report_list[0]._fragment == expected_fragment
    assert report_list[0]._files[0].filename == "pmd_cpd_test_directory/file_a.py"
    return

def test__format_dir(): 
    # arrange
    tool = PMD_CopyPasteDetector()
    path1 = "/app/unit_tests/tools"
    path2 = "/app/unit_tests/tools/"

    # act
    dir1 = tool._format_dir(path1)
    dir2 = tool._format_dir(path2)

    # assert
    assert dir1 == "/app/unit_tests/tools/"
    assert dir2 == "/app/unit_tests/tools/"
    return