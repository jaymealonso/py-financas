from enum import IntEnum, auto
from ..Genericos.TablePrototype import ColumnDefinition, TableColumnsProvider


class CIndex(IntEnum):
    """Índices das colunas da tabela de lançamentos"""

    ID = 0
    SEQ_ORDEM_LINHA = auto()
    NR_REFERENCIA = auto()
    DESCRICAO = auto()
    DESCRICAO_USER = auto()
    DATA = auto()
    CATEGORIA_ID = auto()
    VALOR = auto()
    SALDO = auto()
    REMOVER = auto()
    ANEXOS = auto()
    NR_ANEXOS = auto()


class LancamentosTableColumns(TableColumnsProvider):
    """Colunas da tabela de lançamentos"""

    def __init__(self):
        super().__init__(
            {
                CIndex.ID: ColumnDefinition(title="ID", sql_colname="id", width=90),
                CIndex.SEQ_ORDEM_LINHA: ColumnDefinition(title="Seq Linha", sql_colname="seq_ordem_linha", width=100),
                CIndex.NR_REFERENCIA: ColumnDefinition(title="Número Ref.", sql_colname="nr_referencia", width=100),
                CIndex.DESCRICAO: ColumnDefinition(title="Descrição", sql_colname="descricao", width=500),
                CIndex.DESCRICAO_USER: ColumnDefinition(
                    title="Descrição Usuário", sql_colname="descricao_user", width=100
                ),
                CIndex.DATA: ColumnDefinition(title="Data", sql_colname="data", width=160),
                CIndex.CATEGORIA_ID: ColumnDefinition(title="Categorias", sql_colname="categoria_id", width=260),
                CIndex.VALOR: ColumnDefinition(title="Valor", sql_colname="valor", width=160),
                CIndex.SALDO: ColumnDefinition(title="Saldo", sql_colname="saldo", width=160),
                CIndex.REMOVER: ColumnDefinition(title="Remover", sql_colname="remover", width=100),
                CIndex.ANEXOS: ColumnDefinition(title="Anexos", sql_colname="anexos", width=100),
            }
        )
