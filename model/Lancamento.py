import moment
import dataclasses
from typing import List, Optional
from sqlalchemy.orm import Session
from dataclasses import dataclass
from model.db.db import Database
from model.db.db_orm import Lancamentos as ORMLancamentos
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
                self.__items.append(
                    Lancamento(
                        id=lancamento.id,
                        conta_id=lancamento.conta_id,
                        nr_referencia=lancamento.nr_referencia,
                        descricao=lancamento.descricao,
                        data=moment.date(lancamento.data).date,
                        valor=lancamento.valor,
                        categoria_id=lancamento.Categorias[0].id,
                    )
                )

    def add_new(self, lancam: Lancamento):
        sql = "insert into lancamentos (_id, cont_id, nr_referencia, descricao, data, valor) values(?,?,?,?,?,?)"
        data = dataclasses.astuple(lancam)

        self.__db.execute(sql, data[:6])
        self.__db.commit()

        lancamento_id = self.__db.execute("select last_insert_rowid()").fetchone()
        lancam.id = lancamento_id[0]

    def delete(self, lancamento_id: str):
        sql = "delete from lancamentos where _id = ?"

        self.__db.execute(sql, (lancamento_id,))
        self.__db.commit()

    def update(self, lancamento: Lancamento):
        sql = """
            update lancamentos 
               set conta_id = ?,
                   nr_referencia = ?,
                   descricao = ?,
                   data = ?,
                   valor = ?
             where _id = ?
        """
        self.__db.execute(
            sql,
            (
                lancamento.conta_id,
                lancamento.nr_referencia,
                lancamento.descricao,
                lancamento.data,
                lancamento.valor,
                lancamento.id,
            ),
        )
        sql2 = """
            delete from lancamento_categoria  
             where lancamento_id = ?
        """
        self.__db.execute(sql2, (lancamento.id,))

        if lancamento.categoria_id and lancamento.categoria_id != "0":
            sql3 = """
                INSERT INTO lancamento_categoria (lancamento_id, categoria_id) values (?, ?)
            """
            self.__db.execute(sql3, (lancamento.id, lancamento.categoria_id))

        self.__db.commit()

    def items(self):
        return self.__items
