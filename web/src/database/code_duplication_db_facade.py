from src.models import db
from src.models.model import *
from src.utilities.selector import Selector
from sqlalchemy.orm import Query
from sqlalchemy.engine import Row

class CodeDuplicationDatabaseFacade: 
    def insert_many_fragments(self, fragments : list[CodeFragment]): 
        for cd in fragments:
            db.session.add(cd)
        db.session.commit()

    def insert_many_duplications(self, duplications : list[Duplication]):
        for dups in duplications:
            db.session.add(dups)
        db.session.commit()

    def get_duplication_by_id(self, id : str) -> CodeFragment:
        return db.session.query(CodeFragment).filter_by(id=id).first()
    
    def get_fragments_for_many_file(self, files : list[File]) -> list[tuple[CodeFragment, Duplication]]:
        file_selector = Selector(files, lambda file: str(file.id))

        query : Query = db.session.query(CodeFragment, Duplication)
        query : Query = query.join(Duplication, Duplication.code_fragment_id==CodeFragment.id)
        query : Query = query.filter(Duplication.file_id.in_(file_selector))
        rows : list[Row] = query.all()

        row_selector = Selector(rows, lambda row : (row[0], row[1]))
        fragment_list = list[tuple[CodeFragment, Duplication]](row_selector)
        return fragment_list

    