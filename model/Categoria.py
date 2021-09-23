from typing import List
from dataclasses import dataclass
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
        self.__categorias.append(Categoria(id=0, nm_categoria="(vazio)"))
        for i in result:
            self.__categorias.append(Categoria(*i))

    def items(self):
        return self.__categorias


