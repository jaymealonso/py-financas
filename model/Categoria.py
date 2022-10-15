from typing import List
from dataclasses import dataclass
from sqlalchemy import select
from model.db.db import Database
from model.db.db_orm import Categorias as ORMCategorias


@dataclass(order=True)
class Categoria:
    id: int
    nm_categoria: str


class Categorias:
    def __init__(self):
        self.__categorias: List[Categoria] = []
        self.__db = Database().engine

    def load(self):
        self.__categorias.clear()
        stmt = select(ORMCategorias).order_by(
            ORMCategorias.nm_categoria
        )  # "select * from categorias order by nm_categoria"
        result = self.__db.connect().execute(stmt).fetchall()
        print(f">>> Carregadas {len(result)} categorias.")
        for i in result:
            print(i)
            self.__categorias.append(Categoria(*i))

    def add_new(self, categoria: Categoria):
        sql = "insert into categorias (_id, nm_categoria) values(?,?)"
        data = (categoria.id, categoria.nm_categoria)

        self.__db.connect().execute(sql, data)
        self.__db.commit()

    def update(self, categoria: Categoria):
        sql = """
          update categorias set nm_categoria = ?
          where _id = ?
        """
        self.__db.connect().execute(sql, (categoria.nm_categoria, categoria.id))
        self.__db.commit()

    def items(self):
        return self.__categorias
