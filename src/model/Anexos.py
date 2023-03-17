from typing import List
from model.db.db import Database
from model.db.db_orm import Anexos as ORMAnexos
from sqlalchemy import insert
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

       
    def add_new(self, caminho:str, descricao:str, lancamento_id:int) -> ORMAnexos:
        """
        Adiciona novo anexo ao DB com os dados de entrada enviados
        e retorna o ID do novo anexo
        """
        with Session(self.__db.engine) as session:
            new_anexo = session.scalar(
                insert(ORMAnexos).returning(ORMAnexos),
                [
                    {
                        "descricao": descricao,
                        "caminho": caminho,
                        "lancamento_id": lancamento_id
                    }
                ],
            )
            session.commit()

            return new_anexo