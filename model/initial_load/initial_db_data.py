from sqlalchemy.engine import Engine
from sqlalchemy import insert
from model.db.db_orm import (
    ContasTipo,
    Categorias,
    Contas,
    Lancamentos,
    association_lanc_categ,
)


class DataLoader:
    def __init__(self, db: Engine) -> None:
        self.db = db

    def insert_all(self):
        self.__insert_contas_tipo()
        self.__insert_categorias()

    def __insert_contas_tipo(self):

        stmt = insert(ContasTipo).values(
            [
                {"descricao": "Conta Corrente"},
                {"descricao": "Poupança"},
                {"descricao": "Cartão Crédito"},
            ]
        )

        with self.db.connect() as conn:
            trans = conn.begin()
            conn.execute(stmt)
            trans.commit()

    def __insert_categorias(self):

        stmt = insert(Categorias).values(
            [
                {"nm_categoria": "Almoço"},
                {"nm_categoria": "Aluguel"},
                {"nm_categoria": "Água"},
                {"nm_categoria": "Banco"},
                {"nm_categoria": "Carro"},
                {"nm_categoria": "Cartão Crédito"},
                {"nm_categoria": "Combo TV+Internet"},
                {"nm_categoria": "Comida fora"},
                {"nm_categoria": "Compras"},
                {"nm_categoria": "Entretenimento"},
                {"nm_categoria": "Escola"},
                {"nm_categoria": "Imposto"},
                {"nm_categoria": "Luz"},
                {"nm_categoria": "Multa"},
                {"nm_categoria": "Poupança"},
                {"nm_categoria": "Salário"},
                {"nm_categoria": "Saque"},
                {"nm_categoria": "Segurança Social"},
                {"nm_categoria": "Seguro"},
                {"nm_categoria": "Supermercado"},
                {"nm_categoria": "Transferência"},
                {"nm_categoria": "Transporte"},
            ]
        )

        with self.db.connect() as conn:
            trans = conn.begin()
            conn.execute(stmt)
            trans.commit()

    def insert_sample_db(self):
        self.__insert_contas()
        self.__insert_lancamentos()
        self.__insert_lanc_categoria()
        pass

    def __insert_contas(self):

        stmt = insert(Contas).values(
            [
                {
                    "descricao": "Itaú-CC",
                    "numero": "0516-145589",
                    "moeda": "BRL",
                    "tipo_id": 1,
                },
                {
                    "descricao": "ActivoBank-CC",
                    "numero": "PT144684831",
                    "moeda": "BRL",
                    "tipo_id": 1,
                },
                {
                    "descricao": "ActivoBank-CRD",
                    "numero": "PT144684831",
                    "moeda": "BRL",
                    "tipo_id": 3,
                },
                {
                    "descricao": "BPI-CC",
                    "numero": "4477889-888555",
                    "moeda": "BRL",
                    "tipo_id": 1,
                },
            ]
        )

        with self.db.connect() as conn:
            trans = conn.begin()
            conn.execute(stmt)
            trans.commit()

        pass

    def __insert_lancamentos(self):
        stmt = insert(Lancamentos).values(
            [
                {
                    "conta_id": 1,
                    "nr_referencia": "334562",
                    "descricao": "Transf China",
                    "data": "2019-11-30",
                    "valor": -2200,
                },
                {
                    "conta_id": 1,
                    "nr_referencia": "334563",
                    "descricao": "Transf Port.",
                    "data": "2019-11-30",
                    "valor": -120,
                },
                {
                    "conta_id": 2,
                    "nr_referencia": "334562",
                    "descricao": "Salário",
                    "data": "2019-11-30",
                    "valor": 500000,
                },
                {
                    "conta_id": 2,
                    "nr_referencia": "334563",
                    "descricao": "Compra bala",
                    "data": "2019-11-30",
                    "valor": -10000,
                },
                {
                    "conta_id": 2,
                    "nr_referencia": "334564",
                    "descricao": "Comprar chiclete",
                    "data": "2019-11-30",
                    "valor": -12000,
                },
                {
                    "conta_id": 2,
                    "nr_referencia": "334565",
                    "descricao": "Aluguel",
                    "data": "2019-12-01",
                    "valor": -65050,
                },
                {
                    "conta_id": 2,
                    "nr_referencia": "334566",
                    "descricao": "Carro",
                    "data": "2019-12-02",
                    "valor": -36050,
                },
            ]
        )

        with self.db.connect() as conn:
            trans = conn.begin()
            conn.execute(stmt)
            trans.commit()

    def __insert_lanc_categoria(self):
        stmt = insert(association_lanc_categ).values(
            [
                {"lancamento_id": 1, "categoria_id": 1},
                {"lancamento_id": 2, "categoria_id": 1},
            ]
        )

        with self.db.connect() as conn:
            trans = conn.begin()
            conn.execute(stmt)
            trans.commit()
