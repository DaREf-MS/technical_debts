from src.database.code_duplication_db_facade import CodeDuplicationDatabaseFacade
from src.services.code_duplication_service import CodeDuplicationService
from src.reports.duplication_report import DuplicationReport
from src.utilities.value_range import ValueRange
from src.models.model import *

def test_insert():
    # arrange
    class LocalFacadeMock(CodeDuplicationDatabaseFacade):
        frag_called = 0
        dupl_called = 0
        order_followed = True
        params_valid = True

        def insert_many_fragments(self, fragments):
            LocalFacadeMock.frag_called += 1
            LocalFacadeMock.params_valid &= (len(fragments) == 2)
            LocalFacadeMock.order_followed &= (LocalFacadeMock.dupl_called == 0)
            return
        
        def insert_many_duplications(self, associations):
            LocalFacadeMock.dupl_called += 1
            LocalFacadeMock.params_valid &= (len(associations) == 4)
            LocalFacadeMock.order_followed &= (LocalFacadeMock.frag_called != 0)
            return
    
    mock = LocalFacadeMock()
    service = CodeDuplicationService(mock)
    fragments = [CodeFragment("hello", 10), CodeFragment("world", 11)]
    duplications = [Duplication(fragments[0].id, 'file0', 10, ValueRange(0, 10), ValueRange(0, 10)), 
                    Duplication(fragments[1].id, 'file0', 11, ValueRange(0, 10), ValueRange(0, 10)),
                    Duplication(fragments[0].id, 'file1', 10, ValueRange(0, 10), ValueRange(0, 10)), 
                    Duplication(fragments[1].id, 'file1', 11, ValueRange(0, 10), ValueRange(0, 10))]

    # act 
    service.insert(fragments, duplications)

    # assert
    assert LocalFacadeMock.frag_called == 1
    assert LocalFacadeMock.dupl_called == 1
    assert LocalFacadeMock.params_valid
    assert LocalFacadeMock.order_followed

def test_get_duplication_by_id(): 
    # arrange
    class LocalFacadeMock(CodeDuplicationDatabaseFacade):
        called = False
        params_valid = False

        def get_duplication_by_id(self, id):
            LocalFacadeMock.called = True
            LocalFacadeMock.params_valid = id == 'test_id'
            inst = CodeFragment('test', 10)
            inst.id = 'test_id'
            return inst
    
    mock = LocalFacadeMock()
    service = CodeDuplicationService(mock)

    # act
    result = service.get_fragment_by_id('test_id')

    # assert
    assert LocalFacadeMock.called and LocalFacadeMock.params_valid
    assert result.id == 'test_id' and result.text == 'test'
    assert result.line_count == 10

def test_get_fragments_for_many_file():
    # arrange 
    class LocalFacadeMock(CodeDuplicationDatabaseFacade):
        called = False
        params_valid = False

        def get_fragments_for_many_file(self, file_list):
            LocalFacadeMock.called = True
            LocalFacadeMock.params_valid = (
                file_list[0].id == 'file0' and 
                file_list[1].id == 'file1'
            )
            
            cf0 = CodeFragment("hello", 10)
            cf1 = CodeFragment("world", 20)
            cf0.id = 'c0'
            cf1.id = 'c1'

            return [
                (cf0, Duplication(cf0.id, 'file0', 10, ValueRange(0, 10), ValueRange(0, 10))),
                (cf0, Duplication(cf0.id, 'file1', 10, ValueRange(0, 10), ValueRange(0, 10))),
                (cf1, Duplication(cf1.id, 'file0', 20, ValueRange(0, 10), ValueRange(0, 10))),
                (cf1, Duplication(cf1.id, 'file1', 20, ValueRange(0, 10), ValueRange(0, 10)))
            ]
        
    mock = LocalFacadeMock()
    service = CodeDuplicationService(mock)

    # act
    result = service.get_reports_for_many_files([
        File(id='file0',name='file0.py',commit_id='...'),
        File(id='file1',name='file1.py',commit_id='...')
    ])

    # assert 
    assert LocalFacadeMock.called and LocalFacadeMock.params_valid
    assert "c0" in result
    assert len(result) == 2
    
    report = result['c0']
    assert report.get_lines() == 10
    assert report.get_fragment() == "hello"
    assert len(report._files) == 2
    
    file = report._files[0]
    assert file.filename == 'file0.py'
    assert file.lines.From == 0 and file.lines.To == 10
    assert file.columns.From == 0 and file.columns.To == 10

def test_insert_elements_from_parsed_xml(): 
    # arrange
    class LocalServiceMock(CodeDuplicationService):
        called = False
        params_valid = False

        def __init__(self):
            super().__init__(None)

        def insert(self, fragments, duplications):
            LocalServiceMock.called = True
            LocalServiceMock.params_valid = (len(fragments) == 2) and (len(duplications) == 4)

    files = [
        File(id='file0', name='file0.py', commit_id='...'),
        File(id='file1', name='file1.py', commit_id='...'),
    ]
    report0_files = [
        DuplicationReport.File("file0.py", ValueRange(0, 3), ValueRange(0, 10)),
        DuplicationReport.File("file1.py", ValueRange(10, 13), ValueRange(0, 10))
    ]
    report1_files = [
        DuplicationReport.File("file0.py", ValueRange(0, 5), ValueRange(0, 15)),
        DuplicationReport.File("file1.py", ValueRange(10, 15), ValueRange(0, 15))
    ]

    report0 = DuplicationReport(3, "hello world")
    report1 = DuplicationReport(6, "world hello")

    report0.add_file(report0_files[0])
    report0.add_file(report0_files[1])
    report1.add_file(report1_files[0])
    report1.add_file(report1_files[1])

    reports = [report0, report1]
    service = LocalServiceMock()

    # act
    service.insert_from_report(reports, files)

    # assert
    assert LocalServiceMock.called and LocalServiceMock.params_valid


def test_insert_elements__exception_file_not_in_db(): 
    # arrange
    class LocalServiceMock(CodeDuplicationService):
        called = False
        params_valid = False

        def __init__(self):
            super().__init__(None)

        def insert(self, fragments, duplications):
            LocalServiceMock.called = True
            return

    files = [
        File(id='file0', name='file0.py', commit_id='...'),
        File(id='file1', name='file1.py', commit_id='...'),
    ]
    report0_files = [
        DuplicationReport.File("file0.py", ValueRange(0, 3), ValueRange(0, 10)),
        DuplicationReport.File("file1.py", ValueRange(10, 13), ValueRange(0, 10)),
        DuplicationReport.File("file2.py", ValueRange(3, 39), ValueRange(0, 10))
    ]

    report0 = DuplicationReport(3, "hello world")

    report0.add_file(report0_files[0])
    report0.add_file(report0_files[1])
    report0.add_file(report0_files[2])
    reports = [report0]
    service = LocalServiceMock()

    # act
    try:
        service.insert_from_report(reports, files)
        
    # assert
        assert False
    except Exception as e:
        assert LocalServiceMock.called == False
    return 
    
