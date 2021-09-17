import dataclasses
from dataclasses import dataclass
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


class Contas:
    def __init__(self):
        self.__items = []
        self.__db = Database().db

    def load(self):
        self.__items.clear()
        sql = 'select * from contas'
        result = self.__db.execute(sql).fetchall()
        for i in result:
            self.__items.append(Conta(*i))

    def add_new(self, conta: Conta):
        sql = 'insert into contas (_id, descricao, numero, moeda, tipo) values(?,?,?,?,?)'
        data = dataclasses.astuple(conta)

        self.__db.execute(sql, data)
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
