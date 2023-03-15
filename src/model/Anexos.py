from typing import List
from model.db.db import Database
from model.db.db_orm import Anexos as ORMAnexos
from sqlalchemy.orm import Session


class Anexos:
    def __init__(self, lancamento_id):
        self.__items: List[ORMAnexos] = []
        self.__db = Database()
        self.lancamento_id: int = lancamento_id

    @property
    def items(self) -> List[ORMAnexos]:
        return self.__items

    def load(self) -> None:
        self.__items.clear()
        with Session(self.__db.engine) as session:
            self.__items = (
                session.query(ORMAnexos)
                .filter(ORMAnexos.lancamento_id == self.lancamento_id)
                .all()
            )
