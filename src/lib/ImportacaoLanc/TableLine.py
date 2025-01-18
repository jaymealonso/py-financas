#!
import locale
from lib.Genericos.log import logging

from datetime import datetime
from util.curr_formatter import str_curr_to_int
from PyQt5.QtWidgets import QComboBox
from lib.Genericos.TableLine import TableLine


class ImportarLancamentosTableLine(TableLine):
    LANCAMENTO_COLUMNS = {
        0: {"name": "(vazio)", "sql_colname": ""},
        1: {"name": "Número Ref.", "sql_colname": "nr_referencia"},
        2: {"name": "Descrição", "sql_colname": "descricao"},
        3: {"name": "Descrição Usuário", "sql_colname": "descricao_user"},
        4: {"name": "Data", "sql_colname": "data"},
        5: {"name": "Categorias", "sql_colname": "categoria_id"},
        6: {"name": "Valor", "sql_colname": "valor"},
    }

    def __init__(self, parent_view) -> None:
        from view.imp_lanc_vw import ImportarLancamentosView

        super(TableLine, self).__init__()
        self.parent_view: ImportarLancamentosView = parent_view

    def get_combo(self) -> QComboBox:
        combo = QComboBox()
        for index, value in self.LANCAMENTO_COLUMNS.items():
            name = value["name"]
            sql_colname = value["sql_colname"]
            combo.addItem(name, sql_colname)

        return combo
