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
    """
    Todos os lancamentos de uma conta
    """

    def __init__(self, conta_dc: Conta):
        self.id = None
        self.__items: List[Lancamento] = []
        self.__db = Database().engine
        self.conta: Conta = conta_dc

    @property
    def total(self) -> int:
        """
        Valor total dos lancamentos
        """
        return sum([x.valor for x in self.__items])

    def load(self):
        """
        Carrega dados dos lancamentos do DB
        """
        self.__items.clear()

        with Session(self.__db) as session:
            lancamentos = (
                session.query(ORMLancamentos)
                .filter(ORMLancamentos.conta_id == self.conta.id)
                .order_by(ORMLancamentos.data)
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
        """
        Adiciona novo lancamento ao DB com os dados de entrada enviados
        """
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
        """
        Elimina lancamento com o ID enviado e relação com categorias 
        """
        stmt_delete = delete(ORMLancCateg).where(
            ORMLancCateg.c.lancamento_id == lancamento_id
        )
        stmt = delete(ORMLancamentos).where(ORMLancamentos.id == lancamento_id)

        with self.__db.connect() as conn:
            trans = conn.begin()
            conn.execute(stmt_delete)
            conn.execute(stmt)
            trans.commit()

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

        stmt_delete = delete(ORMLancCateg).where(
            ORMLancCateg.c.lancamento_id == lancamento.id
        )

        with self.__db.connect() as conn:
            trans = conn.begin()
            conn.execute(stmt_update)
            conn.execute(stmt_delete)
            if lancamento.categoria_id != "":
                stmt_insert = insert(ORMLancCateg).values(
                    {
                        "lancamento_id": lancamento.id,
                        "categoria_id": lancamento.categoria_id,
                    }
                )
                conn.execute(stmt_insert)
            trans.commit()

    def items(self):
        return self.__items
