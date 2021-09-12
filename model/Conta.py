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

    def load(self):
        db = Database().db

        result = db.execute('select * from contas').fetchall()
        for i in result:
            self.__items.append(Conta(*i))

    def items(self):
        return self.__items

