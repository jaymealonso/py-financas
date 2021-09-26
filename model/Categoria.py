from typing import List
from dataclasses import dataclass, astuple
from model.db import Database


@dataclass(frozen=True, order=True)
class Categoria:
    id: int
    nm_categoria: str


class Categorias:
    def __init__(self):
        self.__categorias: List[Categoria] = []
        self.__db = Database().db

    def load(self):
        self.__categorias.clear()
        sql = 'select * from categorias'
        result = self.__db.execute(sql,).fetchall()
        print(f"Carregadas {len(result)} categorias.")
        for i in result:
            self.__categorias.append(Categoria(*i))

    def add_new(self, categoria: Categoria):
        sql = 'insert into categoria (_id, nm_categoria) values(?,?)'
        data = astuple(categoria)

        self.__db.execute(sql, data[:5])
        self.__db.commit()

    def items(self):
        return self.__categorias


