import datetime
import dataclasses
from typing import List
from dataclasses import dataclass
from model.db import Database
from model.Conta import Conta
from model.Categoria import Categoria, Categorias


@dataclass
class Lancamento:
    id: str
    conta_id: int
    nr_referencia: str
    descricao: str
    data: datetime.date
    value: float
    categoria_id: int
    # _categorias: Categorias = field(init=False)

    # def __post_init__(self):
    #     pass  # self._categorias =
    #
    # def get_categorias(self):
    #     return self._categorias


class Lancamentos:
    def __init__(self, conta_dc: Conta):
        self.__items: List[Lancamento] = []
        self.__db = Database().db
        self.conta: Conta = conta_dc

    def load(self):
        self.__items.clear()
        sql = '''
            select l.*, c._id as categoria_id from lancamentos as l
                   left join lancamento_categoria as lc on lc.lancamento_id = l._id
                   left join categorias as c on c._id = lc.categoria_id
             where l.conta_id = ?
        '''
        result = self.__db.execute(sql, (self.conta.id,)).fetchall()
        for i in result:
            self.__items.append(Lancamento(*i))

    def add_new(self, lancam: Lancamento):
        sql = 'insert into lancamentos (_id, conta_id, nr_referencia, descricao, data, valor) values(?,?,?,?,?,?)'
        data = dataclasses.astuple(lancam)

        self.__db.execute(sql, data[:6])
        self.__db.commit()

        lancamento_id = self.__db.execute("select last_insert_rowid()").fetchone()
        lancam.id = lancamento_id[0]

    def delete(self, lancamento_id: str):
        sql = 'delete from lancamentos where _id = ?'

        self.__db.execute(sql, (lancamento_id,))
        self.__db.commit()

    def items(self):
        return self.__items











