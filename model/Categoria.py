from typing import List
from dataclasses import dataclass, astuple
from model.db import Database


@dataclass(order=True)
class Categoria:
    id: int
    nm_categoria: str


class Categorias:
    def __init__(self):
        self.__categorias: List[Categoria] = []
        self.__db = Database().db

    def load(self):
        self.__categorias.clear()
        sql = 'select * from categorias order by nm_categoria'
        result = self.__db.execute(sql,).fetchall()
        print(f"Carregadas {len(result)} categorias.")
        for i in result:
            self.__categorias.append(Categoria(*i))

    def add_new(self, categoria: Categoria):
        sql = 'insert into categorias (_id, nm_categoria) values(?,?)'
        data = (categoria.id, categoria.nm_categoria)

        self.__db.execute(sql, data)
        self.__db.commit()

    def update(self, categoria: Categoria):
        sql = ''' 
          update categorias set nm_categoria = ? 
          where _id = ? 
        '''
        self.__db.execute(sql, (categoria.nm_categoria, categoria.id))
        self.__db.commit()

    def items(self):
        return self.__categorias


