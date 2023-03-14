import moment
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy import insert
from model.db.db_orm import (
    ContasTipo,
    Categorias,
    Contas,
    Lancamentos,
    association_lanc_categ,
)

class DataLoader:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def insert_all(self):
        self.__insert_contas_tipo()
        self.__insert_categorias()

    def __insert_contas_tipo(self):
        session = Session(self.engine)
        session.execute(
            insert(ContasTipo),
            [
                {"descricao": "Conta Corrente"},
                {"descricao": "Poupança"},
                {"descricao": "Cartão Crédito"},
            ]
        )
        session.commit()

    def __insert_categorias(self):

        session = Session(self.engine)
        session.execute(
            insert(Categorias),
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
        session.commit()

    def insert_sample_db(self):
        self.__insert_contas()
        self.__insert_lancamentos()
        self.__insert_lanc_categoria()

    def __insert_contas(self):

        session = Session(self.engine)
        session.execute(
            insert(Contas), 
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
            ],
        )
        session.commit()

    def __insert_lancamentos(self):

        session = Session(self.engine)
        session.execute(
            insert(Lancamentos),
            [
                {
                    "conta_id": 1,
                    "seq_ordem_linha": 1,
                    "nr_referencia": "334562",
                    "descricao": "Transf China",
                    "data": moment.date("2019-11-30").date,
                    "valor": -2200,
                },
                {
                    "conta_id": 1,
                    "seq_ordem_linha": 2,                    
                    "nr_referencia": "334563",
                    "descricao": "Transf Port.",
                    "data": moment.date("2019-11-30").date,
                    "valor": -120,
                },
                {
                    "conta_id": 2,
                    "seq_ordem_linha": 1,                    
                    "nr_referencia": "334562",
                    "descricao": "Salário",
                    "data": moment.date("2019-11-30").date,
                    "valor": 500000,
                },
                {
                    "conta_id": 2,
                    "seq_ordem_linha": 2,
                    "nr_referencia": "334563",
                    "descricao": "Compra bala",
                    "data": moment.date("2019-11-30").date,
                    "valor": -10000,
                },
                {
                    "conta_id": 2,
                    "seq_ordem_linha": 3,                    
                    "nr_referencia": "334564",
                    "descricao": "Comprar chiclete",
                    "data": moment.date("2019-11-30").date,
                    "valor": -12000,
                },
                {
                    "conta_id": 2,
                    "seq_ordem_linha": 1,
                    "nr_referencia": "334565",
                    "descricao": "Aluguel",
                    "data": moment.date("2019-12-01").date,
                    "valor": -65050,
                },
                {
                    "conta_id": 2,
                    "seq_ordem_linha": 1,
                    "nr_referencia": "334566",
                    "descricao": "Carro",
                    "data": moment.date("2019-12-02").date,
                    "valor": -36050,
                },
            ]
        )
        session.commit()

    def __insert_lanc_categoria(self):
        session = Session(self.engine)
        session.execute(
            insert(association_lanc_categ),
            [
                {"lancamento_id": 1, "categoria_id": 1},
                {"lancamento_id": 2, "categoria_id": 1},
            ]
        )
        session.commit()
