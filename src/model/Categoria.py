import logging
from typing import List
from sqlalchemy import func, insert, select, update
from sqlalchemy.orm import Session
from model.db.db import Database
from model.db.db_orm import Categorias as ORMCategorias, Lancamentos as ORMLancamentos


class Categorias:
    def __init__(self):
        self.__categorias: List[ORMCategorias] = []
        self.__db = Database()

    @property
    def items(self):
        return self.__categorias

    def load(self):
        self.__categorias.clear()

        categ_vazio = ORMCategorias(id=0, nm_categoria="(vazio)")
        # categ_vazio = (0, "(vazio)", "0")
        categ_vazio.tot_lancamentos = 0
        self.__categorias.append(categ_vazio)

        # TODO: corrigir busca de valores de categoria vazio,
        #  somatoria de nr_lancamentos está errada
        with Session(self.__db.engine) as session:
            result = session.execute(
                select(
                    ORMCategorias.id,
                    ORMCategorias.nm_categoria,
                    func.count(ORMLancamentos.id).label("tot_lancamentos"),
                )
                .join(ORMCategorias.Lancamentos, isouter=True)
                .group_by(ORMCategorias)
            ).all()

            self.__categorias = self.__categorias + result

        logging.debug(f">>> Carregadas {len(self.__categorias)} categorias.")

    def add_new_empty(self) -> int:
        return self.add_new(ORMCategorias(id=None, nm_categoria="Nova Categoria"))

    def add_new(self, categoria: ORMCategorias) -> int:
        """
        Insere nova categoria com nome padrão e retorna o ID do novo registro criado
        """
        stmt = insert(ORMCategorias).values({"nm_categoria": categoria.nm_categoria})

        with self.__db.engine.connect() as conn:
            trans = conn.begin()
            result = conn.execute(stmt)
            trans.commit()

        return result.inserted_primary_key.id

    def update(self, categoria_id: int, fieldname: str, value):
        stmt = (
            update(ORMCategorias)
                .where(ORMCategorias.id == categoria_id)
                .values({fieldname: value})
        )

        with self.__db.engine.connect() as conn:
            trans = conn.begin()
            conn.execute(stmt)
            trans.commit()

    def delete(self, categoria_id: int):
        """
        Elimina categoria com o ID enviado
        """
        with Session(self.__db.engine) as session:
            session.query(ORMCategorias).filter(
                ORMCategorias.id == categoria_id
            ).delete()

            session.commit()
