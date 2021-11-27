from dataclasses import dataclass
from model.db import Database
from model.Conta import Conta
from typing import List


@dataclass
class VisaoGeralRow:
    conta_dc: Conta
    ano_mes: str
    nm_categoria: str
    categoria_id: int
    valor: int
    moeda: str

@dataclass
class VisaoGeralColumn:
    conta_dc: Conta
    ano_mes: str


class VisaoMensal:
    def __init__(self, conta_dc: Conta):
        self.__conta_dc = conta_dc
        self.__db = Database().db
        self.values: List[VisaoGeralRow] = []
        self.columns: List[VisaoGeralColumn] = []

    def load(self):
        self.__load_values()
        self.__load_columns()

    def get_unique_row_labels(self):
        return list(dict.fromkeys([row.nm_categoria for row in self.values]))

    def __load_values(self):
        self.values.clear()
        sql = '''
            select l.conta_id,
                   substr( l.data, 0, 8) as ano_mes,
                   c.nm_categoria, 
                   c._id as categoria_id, 
                   sum( l.valor ) as valor,
                   ct.moeda
              from lancamentos as l
                   inner join contas as ct on ct._id = l.conta_id
                   left outer join lancamento_categoria as lc 
                           on lc.lancamento_id = l._id
                   left outer join categorias as c 
                                on c._id = lc.categoria_id 
             where l.conta_id = ?
             group by conta_id, nm_categoria, categoria_id, ano_mes
             order by conta_id, nm_categoria, categoria_id, ano_mes
        '''
        values = self.__db.execute(sql, (self.__conta_dc.id,)).fetchall()
        self.values = [VisaoGeralRow(*value) for value in values]

    def __load_columns(self):
        self.columns.clear()
        sql = '''
             select l.conta_id,
                    substr( l.data, 0, 8) as ano_mes
               from lancamentos as l
                    left outer join lancamento_categoria as lc 
                                 on lc.lancamento_id = l._id
              where l.conta_id = ?
              group by conta_id, ano_mes
              order by conta_id, ano_mes
         '''

        values = self.__db.execute(sql, (self.__conta_dc.id,)).fetchall()
        self.columns = [VisaoGeralColumn(*value) for value in values]

