import moment
from typing import List, Optional
from sqlalchemy import insert, update, delete, func
from sqlalchemy.orm import Session, joinedload
from dataclasses import dataclass
from model.db.db import Database
from model.db.db_orm import (
    Lancamentos as ORMLancamentos,
    association_lanc_categ as ORMLancCateg,
)
from model.Conta import Conta


class Lancamentos:
    """
    Todos os lancamentos de uma conta
    """

    def __init__(self, conta_dc: Conta):
        self.id = None
        self.__items: List[ORMLancamentos] = []
        self.__db = Database().engine
        self.conta: Conta = conta_dc

    @property
    def items(self) -> list[ORMLancamentos]:
        return self.__items

    @property
    def total(self) -> int:
        """
        Valor total dos lancamentos
        """
        return sum([x.valor for x in self.__items])

    def load(self) -> None:
        """
        Carrega dados dos lancamentos do DB
        """
        self.__items.clear()

        with Session(self.__db) as session:
            self.__items = (
                session.query(ORMLancamentos)
                .filter(ORMLancamentos.conta_id == self.conta.id)
                .order_by(ORMLancamentos.data)
                # se não forçar o carregamento aqui carrega quando referencia o "Categorias"
                .options(joinedload(ORMLancamentos.Categorias))
                .all()
            )

    def add_new_empty(self, conta_id: int) -> int:
        new_lancamento = ORMLancamentos(
            id=None,
            conta_id=conta_id,
            nr_referencia="",
            descricao="",
            data=moment.now(),
            valor=0,
        )
        return self.add_new(new_lancamento)

    def add_new(self, lancam: ORMLancamentos) -> int:
        """
        Adiciona novo lancamento ao DB com os dados de entrada enviados
        e retorna o ID do novo lancamento
        """

        session = Session(self.__db)
        stmt_max_seq_ordem_linha = (
            session.query(func.max(ORMLancamentos.seq_ordem_linha))
            .filter(
                ORMLancamentos.conta_id == lancam.conta_id,
                ORMLancamentos.data == lancam.data.date.date(),
            )
            .first()
        )
        seq_ordem_linha: int = 1
        if stmt_max_seq_ordem_linha[0]:
            seq_ordem_linha = int(stmt_max_seq_ordem_linha[0])

        stmt = insert(ORMLancamentos).values(
            {
                "conta_id": lancam.conta_id,
                "seq_ordem_linha": seq_ordem_linha,
                "nr_referencia": lancam.nr_referencia,
                "descricao": lancam.descricao,
                "data": lancam.data.date.date(),
                "valor": lancam.valor,
            }
        )

        with self.__db.connect() as conn:
            trans = conn.begin()
            result = conn.execute(stmt)
            trans.commit()

        return result.inserted_primary_key.id

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

    def update(self, id: int, column_name: str, value):
        """
        Atualiza somente o que foi modificado, possui um tratamento
        especial para Categoria por que é uma relação n:n
        """
        conn = self.__db.connect()
        session = Session(self.__db)
        trans = conn.begin()
        if column_name == "categoria_id":
            stmt_delete = delete(ORMLancCateg).where(ORMLancCateg.c.lancamento_id == id)
            stmt_insert = insert(ORMLancCateg).values(
                {
                    "lancamento_id": id,
                    "categoria_id": value,
                }
            )
            conn.execute(stmt_delete)
            conn.execute(stmt_insert)
        else:
            stmt_update = (
                update(ORMLancamentos)
                .where(ORMLancamentos.id == id)
                .values({column_name: value})
            )
            conn.execute(stmt_update)

        trans.commit()
