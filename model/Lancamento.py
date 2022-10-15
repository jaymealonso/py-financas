import moment
import dataclasses
from typing import List, Optional
from dataclasses import dataclass
from model.db.db import Database
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
        sql = """
            select l.*, c._id as categoria_id from lancamentos as l
                   left join lancamento_categoria as lc on lc.lancamento_id = l._id
                   left join categorias as c on c._id = lc.categoria_id
             where l.conta_id = ?
             order by l.data
        """
        result = self.__db.execute(sql, (self.conta.id,)).fetchall()
        for i in result:
            self.__items.append(Lancamento(*i))

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
