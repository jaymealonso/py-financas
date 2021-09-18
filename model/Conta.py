import dataclasses
from dataclasses import dataclass, field
from model.db import Database


@dataclass
class ContaTipo:
    id: str
    descricao: str


class ContasTipo:
    def __init__(self):
        self.__items = []
        self.db = Database().db
        self.load()

    def load(self):
        result = self.db.execute('select * from contas_tipo').fetchall()
        for i in result:
            self.__items.append(ContaTipo(*i))

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
        self.__items = []
        self.__db = Database().db

    def load(self):
        self.__items.clear()
        sql = ''' 
            select c._id, c.descricao, c.numero, c.moeda, c.tipo, ifnull(sum(l.valor),0) as total
              from contas as c
                   left join lancamentos as l on l.conta_id = c._id
             group by c._id, c.descricao, c.numero, c.moeda, c.tipo
        '''
        result = self.__db.execute(sql).fetchall()
        for i in result:
            conta = Conta(*i[:5])
            conta.total = i[5]
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

    def items(self):
        return self.__items

    def findById(self, id: str):
        enc_conta = None
        for item in self.__items:
            if str(item.id) == id:
                enc_conta = item
        return enc_conta
