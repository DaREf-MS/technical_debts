
from flask import Flask
from dotenv import load_dotenv
from src.models.model import *
from src.utilities.value_range import ValueRange
import os

REPO = 0
BRANCH = 1
COMMITS = 2
FILES = 3
CODE_FRAGMENTS = 4
DUPLICATION_ASSOCIATIONS = 5
FUNCTIONS = 6
COMPLEXITY = 7
IDENTIFIABLE_ENTITIES = 8
FILE_IDENTIFIABLE_ENTITIES = 9

def start_up() -> tuple[Repository, Branch, list[Commit], list[File], list[CodeFragment], list[Duplication]]:
    # pre-defined values
    repo0 = Repository(id='repo0', owner='test', name='test')
    branch0 = Branch(id='branch0', name='test',repository_id=repo0.id)
    commit_list = [
        Commit(id='commit0', sha='0', date=datetime.now(), author='test', message='test0', branch_id=branch0.id),
        Commit(id='commit1', sha='1', date=datetime.now(), author='test', message='test1', branch_id=branch0.id)
    ]
    file_list = [
        File(id='file0', name='file0.py', commit_id=commit_list[0].id),
        File(id='file1', name='file1.py', commit_id=commit_list[0].id),
        File(id='file2', name='file2.py', commit_id=commit_list[0].id),
        File(id='file3', name='file0.py', commit_id=commit_list[1].id),
        File(id='file4', name='file1.py', commit_id=commit_list[1].id),
        File(id='file5', name='file2.py', commit_id=commit_list[1].id)
    ]

    fragment_list = [
        CodeFragment("hello", 10),
        CodeFragment("world", 10),
    ]

    duplication_list = [
        # file0
        Duplication(fragment_list[0].id, file_list[0].id, 10, ValueRange(0, 10), ValueRange(0, 10)),
        Duplication(fragment_list[1].id, file_list[0].id, 10, ValueRange(0, 10), ValueRange(0, 10)),
        # file1
        Duplication(fragment_list[0].id, file_list[1].id, 10, ValueRange(0, 10), ValueRange(0, 10)),
        Duplication(fragment_list[1].id, file_list[1].id, 10, ValueRange(0, 10), ValueRange(0, 10))
    ]

    function_list = [
        # file0
        Function(id='func0', name='def function0():', line_position=1, file_id=file_list[0].id),
        Function(id='func1', name='def function1():', line_position=1, file_id=file_list[0].id),
        Function(id='func2', name='def function2():', line_position=1, file_id=file_list[0].id),
        Function(id='func3', name='def function3():', line_position=1, file_id=file_list[0].id),
        # file1
        Function(id='func4', name='def function4():', line_position=1, file_id=file_list[1].id),
        Function(id='func5', name='def function5():', line_position=1, file_id=file_list[1].id),
        Function(id='func6', name='def function6():', line_position=1, file_id=file_list[1].id),
        Function(id='func7', name='def function7():', line_position=1, file_id=file_list[1].id),
    ]

    complexity_list = [
        # file0, func0 to func3
        Complexity(id='cplx0', value=5, function_id=function_list[0].id),
        Complexity(id='cplx1', value=10, function_id=function_list[1].id),
        Complexity(id='cplx2', value=15, function_id=function_list[2].id),
        Complexity(id='cplx3', value=25, function_id=function_list[3].id),
        # file1, func4 to func 7
        Complexity(id='cplx4', value=20, function_id=function_list[4].id),
        Complexity(id='cplx5', value=30, function_id=function_list[5].id),
        Complexity(id='cplx6', value=40, function_id=function_list[6].id),
        Complexity(id='cplx7', value=50, function_id=function_list[7].id),
    ]

    # identifiable entities (ie)
    ie_list = [
        IdentifiableEntity(id='ie0', name='test0'),
        IdentifiableEntity(id='ie1', name='test1'),
    ]

    # file identifiable entites (fie)
    fie_list = [
        # file0
        FileIdentifiableEntity(id='fie0',file_id=file_list[0].id, identifiable_entity_id=ie_list[0].id, line_position=3),
        FileIdentifiableEntity(id='fie1',file_id=file_list[0].id, identifiable_entity_id=ie_list[1].id, line_position=7),
        # file1
        FileIdentifiableEntity(id='fie2',file_id=file_list[1].id, identifiable_entity_id=ie_list[0].id, line_position=10),
        FileIdentifiableEntity(id='fie3',file_id=file_list[1].id, identifiable_entity_id=ie_list[1].id, line_position=2),
    ]

    db.drop_all()
    db.create_all()
    db.session.add(repo0)
    db.session.commit()
    db.session.add(branch0)
    db.session.commit()
    db.session.add_all(commit_list)
    db.session.commit()
    db.session.add_all(file_list)
    db.session.commit()
    db.session.add_all(fragment_list)
    db.session.commit()
    db.session.add_all(duplication_list)
    db.session.commit()
    db.session.add_all(function_list)
    db.session.commit()
    db.session.add_all(complexity_list)
    db.session.commit()
    db.session.add_all(ie_list)
    db.session.commit()
    db.session.add_all(fie_list)
    db.session.commit()
    
    return (
        repo0, 
        branch0, 
        commit_list, 
        file_list, 
        fragment_list, 
        duplication_list, 
        function_list, 
        complexity_list,
        ie_list,
        fie_list
    )

def init_mock_app() -> Flask: 
    load_dotenv()
    POSTGRES_USER       = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD   = os.getenv('POSTGRES_PASSWORD', 'postgres')
    POSTGRES_DB         = os.getenv('POSTGRES_DB', 'postgres')
    DATABASE_PORT       = os.getenv('DATABASE_PORT', '5432')
    DATABASE_HOST       = os.getenv('DATABASE_HOST', 'postgres')
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "secret!"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{POSTGRES_DB}'
    app.config['SQLALCHEMY_ENABLE_POOL_PRE_PING'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app