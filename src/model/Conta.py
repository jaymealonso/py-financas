from typing import List
from dataclasses import dataclass
from sqlalchemy import insert, update
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from model import Database, ORMContasTipo, ORMContas


@dataclass
class ContaTipo:
    id: int
    descricao: str


class ContasTipo:
    def __init__(self):
        self.__items: List[ContaTipo] = []
        self.__db = Database()
        self.__load()

    @property
    def items(self):
        return self.__items

    def __load(self):
        self.__items.clear()

        with Session(self.__db.engine) as session:
            contas_tipo = session.query(ORMContasTipo).all()
            for conta_tipo in contas_tipo:
                self.__items.append(ContaTipo(id=conta_tipo.id, descricao=conta_tipo.descricao))


@dataclass
class Conta:
    id: int
    descricao: str
    numero: str
    moeda: str
    tipo_id: str
    lanc_n_class: int
    lanc_classif: int
    total: int


class Contas:
    def __init__(self):
        self.__items: List[Conta] = []
        self.__db = Database()

    @property
    def items(self):
        return self.__items

    def load(self):
        self.__items.clear()
        sql = text(
            """ 
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
        )
        with self.__db.engine.connect() as conn:
            result = conn.execute(sql).all()
            for i in result:
                conta = Conta(
                    id=i.id,
                    numero=i.numero,
                    descricao=i.descricao,
                    moeda=i.moeda,
                    tipo_id=i.tipo_id,
                    lanc_n_class=i.count_n_categ,
                    lanc_classif=i.count_categ,
                    total=i.total,
                )
                self.__items.append(conta)

    def add_new(self, conta: Conta):
        session = Session(self.__db.engine)
        session.execute(
            insert(ORMContas),
            [
                {
                    "descricao": conta.descricao,
                    "numero": conta.numero,
                    "moeda": conta.moeda,
                    "tipo_id": conta.tipo_id,
                },
            ],
        )
        session.commit()

    def delete(self, conta_id: str):
        sql = text("SELECT id FROM lancamentos WHERE conta_id = :conta_id")
        sql_delete_lc = text("DELETE FROM lancamentos_categorias WHERE lancamento_id = :lancamento_id")
        sql_delete = text("DELETE FROM lancamentos WHERE conta_id = :conta_id")
        sql_delete_acc = text("DELETE FROM contas WHERE id = :conta_id")

        with Session(self.__db.engine) as session:
            result = session.execute(sql, {"conta_id": conta_id}).all()
            for (lancamento_id,) in result:
                session.execute(sql_delete_lc, {"lancamento_id": lancamento_id})

            session.execute(sql_delete, {"conta_id": conta_id})

            session.execute(sql_delete_acc, {"conta_id": conta_id})

            session.commit()

    def update(self, conta_id: str, fieldname: str, value):
        session = Session(self.__db.engine)
        session.execute(update(ORMContas).where(ORMContas.id == conta_id).values({fieldname: value}))
        session.commit()

    def find_by_id(self, id: int) -> Conta | None:
        contas_found = [item for item in self.__items if item.id == id]
        return contas_found[0] if len(contas_found) > 0 else None
