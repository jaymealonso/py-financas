from typing import List
from dataclasses import dataclass
from sqlalchemy import select, insert, update
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

    @property
    def items(self):
        return self.__categorias

    def load(self):
        self.__categorias.clear()
        stmt = select(ORMCategorias).order_by(ORMCategorias.nm_categoria)
        result = self.__db.connect().execute(stmt).fetchall()
        print(f">>> Carregadas {len(result)} categorias.")
        self.__categorias.append(Categoria(id=0, nm_categoria="(vazio)"))
        for i in result:
            self.__categorias.append(Categoria(*i))

    def add_new(self, categoria: Categoria):
        stmt = insert(ORMCategorias).values({"nm_categoria": categoria.nm_categoria})

        with self.__db.connect() as conn:
            trans = conn.begin()
            conn.execute(stmt)
            trans.commit()

    def update(self, categoria: Categoria):
        stmt = (
            update(ORMCategorias)
            .where(ORMCategorias.id == categoria.id)
            .values({"nm_categoria": categoria.nm_categoria})
        )

        with self.__db.connect() as conn:
            trans = conn.begin()
            conn.execute(stmt)
            trans.commit()
