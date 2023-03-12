from typing import List
from dataclasses import dataclass, field
from sqlalchemy import insert, update
from sqlalchemy.orm import Session
from model.db.db import Database
from model.db.db_orm import ContasTipo as ORMContasTipo, Contas as ORMContas


@dataclass
class ContaTipo:
    id: int
    descricao: str


class ContasTipo:
    def __init__(self):
        self.__items: List[ContaTipo] = []
        self.__db = Database().engine
        self.__load()

    @property
    def items(self):
        return self.__items

    def __load(self):
        self.__items.clear()

        with Session(self.__db) as session:
            contas_tipo = session.query(ORMContasTipo)
            for conta_tipo in contas_tipo:
                self.__items.append(
                    ContaTipo(id=conta_tipo.id, descricao=conta_tipo.descricao)
                )


@dataclass
class Conta:
    id: str
    descricao: str
    numero: str
    moeda: str
    tipo_id: str
    lanc_n_class: int = field(init=False)
    lanc_classif: int = field(init=False)
    total: int = field(init=False)

    def __post_init__(self):
        self.total = 0
        self.lanc_n_class = 0
        self.lanc_classif = 0


class Contas:
    def __init__(self):
        self.__items: List[Conta] = []
        self.__db = Database().engine

    @property
    def items(self):
        return self.__items

    def load(self):
        self.__items.clear()
        sql = """ 
            select c.id, c.descricao, c.numero, c.moeda, c.tipo_id,
				( select ifnull(sum(l.valor),0)
					from lancamentos as l 
				where l.conta_id = c.id ) as total,
				( select count(*) 
					from lancamentos as l 
						left outer join lancamentos_categorias as lc on lc.lancamento_id = l.id
				where l.conta_id = c.id 
					and lc.lancamento_id is null ) as count_n_categ,
				( select count(*) 
					from lancamentos as l1 
						inner join lancamentos_categorias as lc1 on lc1.lancamento_id = l1.id
            where l1.conta_id = c.id ) as count_categ		
              from contas as c
        """
        with self.__db.connect() as conn:
            result = conn.execute(sql)
            for i in result:
                conta = Conta(*i[:5])
                conta.total = i[5]
                conta.lanc_n_class = i[6]
                conta.lanc_classif = i[7]
                self.__items.append(conta)

    def add_new(self, conta: Conta):
        stmt = insert(ORMContas).values(
            {
                "descricao": conta.descricao,
                "numero": conta.numero,
                "moeda": conta.moeda,
                "tipo_id": conta.tipo_id,
            }
        )

        with self.__db.connect() as conn:
            trans = conn.begin()
            conn.execute(stmt)
            trans.commit()

    def delete(self, conta_id: str):
        with Session(self.__db) as session:
            session.query(ORMContas).filter_by(id=conta_id).delete()
            session.commit()

    def update(self, conta_id: str, fieldname: str, value):
        stmt = (
            update(ORMContas)
            .where(ORMContas.id == conta_id)
            .values(
                {
                    fieldname: value
                    # "descricao": conta.descricao,
                    # "numero": conta.numero,
                    # "moeda": conta.moeda,
                    # "tipo_id": conta.tipo_id,
                }
            )
        )

        with self.__db.connect() as conn:
            trans = conn.begin()
            conn.execute(stmt)
            trans.commit()

    def find_by_id(self, id: str):
        enc_conta = None
        for item in self.__items:
            if str(item.id) == id:
                enc_conta = item
        return enc_conta
