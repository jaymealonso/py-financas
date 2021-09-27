from model.db import Database
from model.Conta import Conta


class VisaoMensal:
    def __init__(self, conta_dc: Conta):
        self.__conta_dc = conta_dc
        self.__db = Database().db
        self.values = []
        self.columns = []

    def load(self):
        self.values.clear()
        self.columns.clear()

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
        self.values = self.__db.execute(sql, (self.__conta_dc.id,)).fetchall()

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
        self.columns = self.__db.execute(sql, (self.__conta_dc.id,)).fetchall()
        self.columns.insert(0, (self.__conta_dc.id, "Categoria"))



