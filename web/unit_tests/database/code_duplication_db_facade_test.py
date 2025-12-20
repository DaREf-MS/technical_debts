from unit_tests.mock_app import *
from src.database.code_duplication_db_facade import CodeDuplicationDatabaseFacade
from src.models.model import *

def test_insert_many_fragments(): 
    app = init_mock_app()
    with app.app_context():
        # arrange
        facade = CodeDuplicationDatabaseFacade()
        fragments = [
            CodeFragment("hello world", 10),
            CodeFragment("world hello", 10)
        ]
  
        # act
        try:
            facade.insert_many_fragments(fragments)

        # assert
        except Exception as e: 
            print(e)
            assert False
    return

def test_insert_many_duplications(): 
    app = init_mock_app()
    with app.app_context():
        # arrange
        predef = start_up()
        facade = CodeDuplicationDatabaseFacade()
        file1 = predef[FILES][0]
        file2 = predef[FILES][1]
        fragments = predef[CODE_FRAGMENTS][0]
        duplications = [
            Duplication(fragments.id, file1.id, 10, ValueRange(0, 10), ValueRange(0, 10)),
            Duplication(fragments.id, file2.id, 20, ValueRange(0, 10), ValueRange(0, 10))
        ]
    
        # act
        try:
            facade.insert_many_duplications(duplications)

        # assert
        except Exception as e: 
            print(e)
            assert False
    return

def test_get_duplication_by_id():
    app = init_mock_app()
    with app.app_context():
        # arrange
        predef = start_up()
        facade = CodeDuplicationDatabaseFacade()
        fragments = predef[CODE_FRAGMENTS][0]

        try:
            # act
            result = facade.get_duplication_by_id(fragments.id)
    
            # assert
            assert result != None and result.text == fragments.text
        except Exception as e:
            print(e)
            assert False
    return

def test_get_fragments_for_many_file():
    app = init_mock_app()
    with app.app_context():
        # arrange
        predef = start_up()
        facade = CodeDuplicationDatabaseFacade()
        files = predef[FILES]
        
        # act 
        try:
            result = facade.get_fragments_for_many_file(files)

        # assert
            assert len(result) == 4
            fragment = result[0][0]
            duplication = result[0][1]
            assert fragment.line_count == 10 and duplication.line_count == 10
            assert fragment.text == 'hello'
            assert duplication.code_fragment_id == fragment.id and duplication.file_id in {'file0', 'file1'}
            assert duplication.from_column == 0 and duplication.to_column == 10
            assert duplication.from_line == 0 and duplication.to_line == 10
        except Exception as e:
            print(e)
            assert False
    return
