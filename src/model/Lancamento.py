from datetime import date
import datetime
import moment
from typing import List
from sqlalchemy import insert, update, delete, func, select
from sqlalchemy.orm import Session, joinedload
from model import Database, ORMLancamentos, ORMLancCateg, ORMAnexos

from sqlalchemy.sql import text


class Lancamentos:
    """Todos os lancamentos de uma conta"""

    def __init__(self):
        self.id = None
        self.__items: List[ORMLancamentos] = []
        self.__db = Database()
        # self.conta: Conta = conta_dc

    @property
    def items(self) -> list[ORMLancamentos]:
        return self.__items

    def get_lancamento(self, lancamento_id: int) -> ORMLancamentos | None:
        items = [item for item in self.items if item.id == lancamento_id]
        if len(items) > 0:
            return items[0]
        else:
            return None

    @property
    def total(self) -> int:
        """
        Valor total dos lancamentos
        """
        return sum([x.valor for x in self.__items])

    def load(self, conta_id: int) -> None:
        """
        Carrega dados dos lancamentos do DB
        """
        self.__items.clear()

        with Session(self.__db.engine) as session:
            self.__items = (
                session.query(ORMLancamentos)
                .filter(ORMLancamentos.conta_id == conta_id)
                .order_by(ORMLancamentos.data, ORMLancamentos.seq_ordem_linha)
                # se não forçar o carregamento aqui carrega quando referencia o "Categorias"
                .options(joinedload(ORMLancamentos.Categorias))
                .all()
            )

            result = session.execute(
                select(ORMLancamentos.id, func.count(ORMAnexos.id).label("nr_anexos"))
                .join(ORMLancamentos.Anexos, isouter=True)
                .filter(ORMLancamentos.conta_id == conta_id)
                .group_by(ORMLancamentos)
            ).all()

            for item in self.items:
                found = next((i for i in result if i.id == item.id), (0, 0))
                item.nr_anexos = found[1]

    def add_new_empty(self, conta_id: int) -> int:
        return self.add_new(
            conta_id=conta_id,
            nr_referencia="",
            descricao="",
            descricao_user="",
            data=moment.now().date.date(),
            valor=0,
        )

    def add_new(
        self, conta_id: int, nr_referencia: str, descricao: str, descricao_user: str, data: date, valor: int
    ) -> int:
        """
        Adiciona novo lancamento ao DB com os dados de entrada enviados
        e retorna o ID do novo lancamento
        """
        seq_ordem_linha = self._get_next_seq(data, conta_id)

        with Session(self.__db.engine) as session:
            new_lancamento = session.scalar(
                insert(ORMLancamentos).returning(ORMLancamentos),
                [
                    {
                        "conta_id": conta_id,
                        "seq_ordem_linha": seq_ordem_linha,
                        "nr_referencia": nr_referencia,
                        "descricao": descricao,
                        "descricao_user": descricao_user,
                        "data": data,
                        "valor": valor,
                    }
                ],
            )
            session.commit()

            return new_lancamento.id

    def _get_next_seq(self, data: datetime.date, conta_id: int) -> int:
        """Busca o próximo numero de sequencial para o mesma data + conta_id"""

        sql = text("""
            select coalesce(max(seq_ordem_linha), 0) + 1000 as next_no
			  from lancamentos 
			  where data = :data
			    and conta_id = :conta_id
         """)
        data: str = f"{data.isoformat()} 00:00:00.000000"
        with self.__db.engine.connect() as conn:
            value = conn.execute(sql, {"data": data, "conta_id": conta_id}).first()

        return value[0]

        # # remove o time do date pra fazer a comparação
        # data: str = f"{data.isoformat()} 00:00:00.000000"
        # stmt_max_seq_ordem_linha = (
        #     session.query(func.max(ORMLancamentos.id))
        #     # .filter(
        #     #     ORMLancamentos.conta_id == conta_id,
        #     #     # ORMLancamentos.data == data,
        #     # )
        #     .first()
        # )
        # seq_ordem_linha: int = 1
        # if stmt_max_seq_ordem_linha[0]:
        #     seq_ordem_linha = int(stmt_max_seq_ordem_linha[0]) + 1
        # return seq_ordem_linha

    def delete(self, lancamento_id: str):
        """
        Elimina lancamento com o ID enviado e relação com categorias
        """
        with Session(self.__db.engine) as session:
            session.query(ORMLancCateg).filter(ORMLancCateg.c.lancamento_id == lancamento_id).delete()
            session.query(ORMLancamentos).filter(ORMLancamentos.id == lancamento_id).delete()

            session.commit()

    def update(self, id: int, column_name: str, value):
        """
        Atualiza somente o que foi modificado, possui um tratamento
        especial para Categoria por que é uma relação n:n
        """
        conn = self.__db.engine.connect()
        trans = conn.begin()
        if column_name == "categoria_id":
            stmt_delete = delete(ORMLancCateg).where(ORMLancCateg.c.lancamento_id == id)
            conn.execute(stmt_delete)
            if value > 0:
                stmt_insert = insert(ORMLancCateg).values(
                    {
                        "lancamento_id": id,
                        "categoria_id": value,
                    }
                )
                conn.execute(stmt_insert)
        else:
            stmt_update = update(ORMLancamentos).where(ORMLancamentos.id == id).values({column_name: value})
            conn.execute(stmt_update)

        trans.commit()

    def update_seq_ordem_linha(self, moving_lanc_id: int, prev_lanc_id: int, next_lanc_id: int) -> None:
        if not prev_lanc_id:
            return

        # Busca todos os registros com a mesma data do lancamento que está sendo movido
        sql = text("""
            select l.* from lancamentos as l
			inner join (
                select data, conta_id from lancamentos where id = :lancamento_id
            )  as x on x.data = l.data and x.conta_id = l.conta_id
			order by l.data, l.seq_ordem_linha 
         """)
        with self.__db.engine.connect() as conn:
            values = conn.execute(sql, {"lancamento_id": moving_lanc_id}).all()

        index_moving = next((index for index, value in enumerate(values) if value.id == moving_lanc_id), 0)

        moving_record = values.pop(index_moving)

        index_prev = next((index for index, value in enumerate(values) if value.id == prev_lanc_id), 0)

        values.insert(index_prev + 1, moving_record)

        seq_ordem_linha = 0
        for value in values:
            seq_ordem_linha += 1000

            self.update(value.id, "seq_ordem_linha", seq_ordem_linha)

    def get_next_nr_seq(self, data: datetime.date) -> int:
        sql = text("""
            select max( seq_ordem_linha ) from lancamentos 
              where data = :data
        """)
        with self.__db.engine.connect() as conn:
            value = conn.execute(sql, {"data": data}).first()
            if not value:
                value = 0
            value += 1000

        return value
