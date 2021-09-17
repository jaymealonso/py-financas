import datetime
import dataclasses
from dataclasses import dataclass
from model.db import Database
from model.Conta import Conta


@dataclass
class Lancamento:
    id: str
    conta_id: int
    nr_referencia: str
    descricao: str
    data: datetime.date
    value: float


class Lancamentos:
    def __init__(self, conta_dc: Conta):
        self.__items = []
        self.__db = Database().db
        self.conta: Conta = conta_dc

    def load(self):
        self.__items.clear()
        sql = 'select * from lancamentos where conta_id = ?'
        result = self.__db.execute(sql, (self.conta.id,)).fetchall()
        for i in result:
            self.__items.append(Lancamento(*i))

    def add_new(self, lancam: Lancamento):
        sql = 'insert into lancamentos (_id, conta_id, nr_referencia, descricao, data, valor) values(?,?,?,?,?,?)'
        data = dataclasses.astuple(lancam)

        self.__db.execute(sql, data)
        self.__db.commit()

    def delete(self, lancamento_id: str):
        sql = 'delete from lancamentos where _id = ?'

        self.__db.execute(sql, (lancamento_id,))
        self.__db.commit()

    def items(self):
        return self.__items








