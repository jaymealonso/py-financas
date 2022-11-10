import moment
from typing import List, Optional
from sqlalchemy import insert, update, delete
from sqlalchemy.orm import Session
from dataclasses import dataclass
from model.db.db import Database
from model.db.db_orm import (
    Lancamentos as ORMLancamentos,
    association_lanc_categ as ORMLancCateg,
)
from model.Conta import Conta


@dataclass
class Lancamento:
    id: Optional[str]
    conta_id: int
    nr_referencia: str
    descricao: str
    data: moment.now().date
    valor: int
    categoria_id: Optional[int]


class Lancamentos:
    def __init__(self, conta_dc: Conta):
        self.id = None
        self.__items: List[Lancamento] = []
        self.__db = Database().engine
        self.conta: Conta = conta_dc

    def load(self):
        self.__items.clear()

        with Session(self.__db) as session:
            lancamentos = (
                session.query(ORMLancamentos)
                .filter(ORMLancamentos.conta_id == self.conta.id)
                .all()
            )
            for lancamento in lancamentos:
                categ_id: str = ""
                if len(lancamento.Categorias) > 0:
                    categ_id = lancamento.Categorias[0].id
                self.__items.append(
                    Lancamento(
                        id=lancamento.id,
                        conta_id=lancamento.conta_id,
                        nr_referencia=lancamento.nr_referencia,
                        descricao=lancamento.descricao,
                        data=moment.date(lancamento.data).date,
                        valor=lancamento.valor,
                        categoria_id=categ_id,
                    )
                )

    def add_new(self, lancam: Lancamento):
        stmt = insert(ORMLancamentos).values(
            {
                "conta_id": lancam.conta_id,
                "nr_referencia": lancam.nr_referencia,
                "descricao": lancam.descricao,
                "data": lancam.data,
                "valor": lancam.valor,
            }
        )

        with self.__db.connect() as conn:
            trans = conn.begin()
            conn.execute(stmt)
            trans.commit()

    def delete(self, lancamento_id: str):
        sql = "delete from lancamentos where _id = ?"

        self.__db.execute(sql, (lancamento_id,))
        self.__db.commit()

    def update(self, lancamento: Lancamento):

        stmt_update = (
            update(ORMLancamentos)
            .where(ORMLancamentos.id == lancamento.id)
            .values(
                {
                    "conta_id": lancamento.conta_id,
                    "nr_referencia": lancamento.nr_referencia,
                    "descricao": lancamento.descricao,
                    "data": lancamento.data,
                    "valor": lancamento.valor,
                }
            )
        )

        with Session(self.__db) as session:
            session.query(ORMLancCateg).filter_by(lancamento_id=lancamento.id).delete()

        # stmt_delete = delete(ORMLancCateg).where(
        #      ORMLancCateg.lancamento_id == lancamento.id
        #  )
        stmt_insert = insert(ORMLancCateg).values(
            {
                "lancamento_id": lancamento.id,
                "categoria_id": lancamento.categoria_id,
            }
        )

        with self.__db.connect() as conn:
            trans = conn.begin()
            conn.execute(stmt_update)
            # conn.execute(stmt_delete)
            conn.execute(stmt_insert)
            trans.commit()

        # sql = """
        #     update lancamentos
        #        set conta_id = ?,
        #            nr_referencia = ?,
        #            descricao = ?,
        #            data = ?,
        #            valor = ?
        #      where _id = ?
        # """
        # self.__db.execute(
        #     sql,
        #     (
        #         lancamento.conta_id,
        #         lancamento.nr_referencia,
        #         lancamento.descricao,
        #         lancamento.data,
        #         lancamento.valor,
        #         lancamento.id,
        #     ),
        # )
        # sql2 = """
        #     delete from lancamento_categoria
        #      where lancamento_id = ?
        # """
        # self.__db.execute(sql2, (lancamento.id,))
        #
        # if lancamento.categoria_id and lancamento.categoria_id != "0":
        #     sql3 = """
        #         INSERT INTO lancamento_categoria (lancamento_id, categoria_id) values (?, ?)
        #     """
        #     self.__db.execute(sql3, (lancamento.id, lancamento.categoria_id))
        #
        # self.__db.commit()

    def items(self):
        return self.__items
