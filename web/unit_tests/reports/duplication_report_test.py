from src.reports.duplication_report import *

def test_add_file():
    # arrange
    report = DuplicationReport(0, "")
    file = DuplicationReport.File("123.py", ValueRange(0, 1), ValueRange(0, 1))

    # act
    report.add_file(file)

    # assert
    assert len(report._files) == 1
    assert report._files[0].filename == file.filename
    assert report._files[0].lines.From == 0
    assert report._files[0].lines.To == 1
    assert report._files[0].columns.From == 0
    assert report._files[0].columns.To == 1

def test_iterator():
    # arrange
    report = DuplicationReport(0, "")
    file0 = DuplicationReport.File("123.py", ValueRange(0, 1), ValueRange(0, 1))
    file1 = DuplicationReport.File("456.py", ValueRange(0, 2), ValueRange(0, 2))

    report.add_file(file0)
    report.add_file(file1)

    # act
    file_list = []
    for file in report:
        file_list.append(file)

    # assert
    assert len(file_list) == 2
    assert file_list[0] == file0
    assert file_list[1] == file1

def test_get_file_nb():
    # arrange
    report = DuplicationReport(1, "test")
    report.add_file(DuplicationReport.File("abc.py", ValueRange(0, 1), ValueRange(0, 1)))
    report.add_file(DuplicationReport.File("def.py", ValueRange(0, 1), ValueRange(0, 1)))

    # act
    result = report.get_file_nb()

    # assert
    assert result == 2
    