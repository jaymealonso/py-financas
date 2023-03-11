from dataclasses import dataclass
from model.db.db import Database
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
        self.__db = Database().engine
        self.values: List[VisaoGeralRow] = []
        self.columns: List[VisaoGeralColumn] = []

    def load(self):
        self.__load_values()
        self.__load_columns()

    def get_unique_row_labels(self):
        return list(dict.fromkeys([row.nm_categoria for row in self.values]))

    def __load_values(self):
        """
        Carrega dados que irão preencher a tabela, conteúdo.
        """
        self.values.clear()
        sql = '''
        select l.conta_id,
               substr( l.data, 0, 8) as ano_mes,
               c.nm_categoria, 
               c.id as categoria_id, 
               sum( l.valor ) as valor,
               ct.moeda
          from lancamentos as l
               inner join contas as ct on ct.id = l.conta_id
               left outer join lancamentos_categorias as lc 
                       on lc.lancamento_id = l.id
               left outer join categorias as c 
                            on c.id = lc.categoria_id 
             where l.conta_id = :conta_id
             group by conta_id, nm_categoria, categoria_id, ano_mes
             order by conta_id, nm_categoria, categoria_id, ano_mes
        '''
        with self.__db.connect() as conn:
            values = conn.execute(sql, {"conta_id": self.__conta_dc.id})
            self.values = [VisaoGeralRow(*value) for value in values]

    def __load_columns(self):
        """
        Carrega numero de colunas que irão aparecer, baseado nos meses com  movimento
        """
        self.columns.clear()
        sql = '''
             select l.conta_id,
                    substr( l.data, 0, 8) as ano_mes
               from lancamentos as l
                    left outer join lancamentos_categorias as lc 
                                 on lc.lancamento_id = l.id
              where l.conta_id = :conta_id
              group by conta_id, ano_mes
              order by conta_id, ano_mes

         '''
        with self.__db.connect() as conn:
            values = conn.execute(sql, {"conta_id": self.__conta_dc.id})
            self.columns = [VisaoGeralColumn(*value) for value in values]
