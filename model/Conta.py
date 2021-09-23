import dataclasses
from typing import List
from dataclasses import dataclass, field
from model.db import Database


@dataclass
class ContaTipo:
    id: int
    descricao: str


class ContasTipo:
    def __init__(self):
        self.__items: dict[str, ContaTipo] = {}
        self.db = Database().db
        self.load()

    def load(self):
        cursor = self.db.execute('select * from contas_tipo')
        # col_names = cursor.description
        result = cursor.fetchall()
        for i in result:
            row = ContaTipo(*i)
            self.__items[row.id] = row

    def items(self):
        return self.__items

    def getByKey(self, i:int):
        for key, item in enumerate(self.__items):
            if item.id == i:
                return item
        return None


@dataclass
class Conta:
    id: str
    descricao: str
    numero: str
    moeda: str
    tipo_id: str
    _lanc_n_class: int = field(init=False)
    _lanc_classif: int = field(init=False)
    _total: float = field(init=False)

    def __post_init__(self):
        self.total = 0
        self.lanc_n_class = 0
        self.lanc_classif = 0

    @property
    def lanc_classif(self) -> int:
        return self._lanc_classif

    @lanc_classif.setter
    def lanc_classif(self, v: int) -> None:
        self._lanc_classif = v

    @property
    def lanc_n_class(self) -> int:
        return self._lanc_n_class

    @lanc_n_class.setter
    def lanc_n_class(self, v: int) -> None:
        self._lanc_n_class = v

    @property
    def total(self) -> float:
        return self._total

    @total.setter
    def total(self, v: float) -> None:
        self._total = v


class Contas:
    def __init__(self):
        self.__items: List[Conta] = []
        self.__db = Database().db

    def load(self):
        self.__items.clear()
        sql = ''' 
            select c._id, c.descricao, c.numero, c.moeda, c.tipo,
				( select ifnull(sum(l.valor),0) 
					from lancamentos as l 
				where l.conta_id = c._id ) as total,
				( select count(*) 
					from lancamentos as l 
						left outer join lancamento_categoria as lc on lc.lancamento_id = l._id
				where l.conta_id = c._id 
					and lc.lancamento_id is null ) as count_n_categ,
				( select count(*) 
					from lancamentos as l1 
						inner join lancamento_categoria as lc1 on lc1.lancamento_id = l1._id
            where l1.conta_id = c._id ) as count_categ		
              from contas as c
        '''
        result = self.__db.execute(sql).fetchall()
        for i in result:
            conta = Conta(*i[:5])
            conta.total = i[5]
            conta.lanc_n_class = i[6]
            conta.lanc_classif = i[7]
            self.__items.append(conta)

    def add_new(self, conta: Conta):
        sql = 'insert into contas (_id, descricao, numero, moeda, tipo) values(?,?,?,?,?)'
        data = dataclasses.astuple(conta)

        self.__db.execute(sql, data[:5])
        self.__db.commit()

    def delete(self, conta_id: str):
        sql = 'delete from contas where _id = ?'

        self.__db.execute(sql, (conta_id,))
        self.__db.commit()

    def update(self, conta: Conta):
        sql = '''
            update contas  
               set descricao = ?,
                   numero = ?,
                   moeda = ?,
                   tipo = ?
             where _id = ?
        '''

        self.__db.execute(sql, (conta.descricao, conta.numero, conta.moeda, conta.tipo_id, conta.id))
        self.__db.commit()

    def items(self):
        return self.__items

    def find_by_id(self, id: str):
        enc_conta = None
        for item in self.__items:
            if str(item.id) == id:
                enc_conta = item
        return enc_conta
