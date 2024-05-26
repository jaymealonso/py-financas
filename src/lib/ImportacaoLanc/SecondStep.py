#!

from enum import IntEnum, auto

from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QTableView, QToolBar, QVBoxLayout, QWidget

import util.curr_formatter as curr
from lib.ImportacaoLanc.FirstStep import NewLancamento
import view.icons.icons as icons
from model.Categoria import Categorias

class SecondStepFrame(QWidget):
    import_linhas = pyqtSignal(list)
    passo_anterior = pyqtSignal()

    class Column(IntEnum):
        NR_REFERENCIA = 0
        DESCRICAO = auto()
        DESCRICAO_USER = auto()
        DATA = auto()
        CATEGORIA_ID = auto()
        VALOR = auto()
        NEW_ID = auto()
        STATUS_IMPORT = auto()

    COLUMNS = {
        Column.NR_REFERENCIA: { "title": "Número Ref.", "sql_colname": "nr_referencia", "col_width": 100 },
        Column.DESCRICAO: {"title": "Descrição", "sql_colname": "descricao", "col_width": 500},
        Column.DESCRICAO_USER: {"title": "Descrição Usuário", "sql_colname": "descricao_user", "col_width": 100},
        Column.DATA: {"title": "Data", "sql_colname": "data", "col_width": 160},
        Column.CATEGORIA_ID: {"title": "Categorias", "sql_colname": "categoria_id", "col_width": 260},
        Column.VALOR: {"title": "Valor", "sql_colname": "valor", "col_width": 160},
        Column.NEW_ID: {"title": "Novo ID", "sql_colname": "id", "col_width": 90 },
        Column.STATUS_IMPORT: {"title": "Estado da Importação", "sql_colname": "valor", "col_width": 400},
    }

    def __init__(self, parent: QWidget) -> None:
        super(SecondStepFrame, self).__init__(parent)

        # local vars
        self.table = self.get_table()
        self.toolbar = QToolBar()
        self.linhas = list[NewLancamento]

        # layout
        layout = QVBoxLayout()
        layout.addWidget(self.get_toolbar())
        layout.addWidget(self.table)

        self.setLayout(layout)

        # model
        self.model_categorias = Categorias()
        self.model_categorias.load()        

        parent.importacao_finalizada.connect(self.set_linhas)

    def get_toolbar(self) -> QToolBar:
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        btn_previous = self.toolbar.addAction(icons.results_prev(), "Passo anterior")
        btn_previous.triggered.connect( self.passo_anterior.emit )

        btn_import_lanc = self.toolbar.addAction(icons.excel_imports(), "Importar linhas")
        btn_import_lanc.triggered.connect( self.on_import_linhas )

        return self.toolbar

    def get_table(self) -> QTableView:
        """
        Retorna tabela com o seu layout
        """
        self.table = QTableView()

        model = QStandardItemModel(0, len(self.COLUMNS))
        model.setHorizontalHeaderLabels([col["title"] for col in self.COLUMNS.values()])

        self.table.setModel(model)
        self.table.setSortingEnabled(True)

        return self.table
    
    def load_table_data(self):
        # reset sort order
        self.table.sortByColumn(-1, Qt.AscendingOrder)

        self.load_model_only()
        self.set_column_default_sizes()

    def load_model_only(self):
        model:QStandardItemModel = self.table.model()
        model.setRowCount(len(self.linhas))
        vertical_col_indexes = []
        for (new_index, row) in enumerate(self.linhas):
            vertical_col_indexes.append(str(row.row_index))
            # model.setItemData(
            #     model.index(new_index, self.Column.ID),
            #     {Qt.DisplayRole: new_index},
            # )
            # model.setItemData(
            #     model.index(new_index, self.Column.SEQ_ORDEM_LINHA),
            #     {Qt.UserRole: row.seq_ordem_linha},
            # )
            model.setItemData(
                model.index(new_index, self.Column.NR_REFERENCIA),
                {Qt.DisplayRole: row.nr_referencia, Qt.UserRole: row.nr_referencia},
            )
            model.setItemData(
                model.index(new_index, self.Column.DESCRICAO),
                {Qt.DisplayRole: row.descricao, Qt.UserRole: row.descricao},
            )
            model.setItemData(
                model.index(new_index, self.Column.DESCRICAO_USER),
                {Qt.DisplayRole: row.descricao_user, Qt.UserRole: row.descricao_user},
            )
            model.setItemData(
                model.index(new_index, self.Column.DATA),
                {Qt.DisplayRole: row.data.strftime("%x"), Qt.UserRole: row.data},
            )
            nm_categoria = next((x.nm_categoria for x in self.model_categorias.items 
                if x.id == row.categoria_id), "<<Categoria não encontrada>>")
            model.setItemData(
                model.index(new_index, self.Column.CATEGORIA_ID),
                {
                    Qt.DisplayRole: nm_categoria,
                    # Qt.UserRole: categoria.id or -1,
                },
            )
            model.setItemData(
                model.index(new_index, self.Column.VALOR),
                {
                    Qt.DisplayRole: curr.str_curr_to_locale(row.valor or 0),
                    Qt.UserRole: row.valor or 0,
                },
            )

            model.setItemData(
                model.index(new_index, self.Column.NEW_ID),
                { Qt.DisplayRole: row.id },
            )
            model.setItemData(
                model.index(new_index, self.Column.STATUS_IMPORT),
                { Qt.DisplayRole: row.status_import },
            )

        model.setVerticalHeaderLabels(vertical_col_indexes)
        self.table.setModel(model)

    def set_column_default_sizes(self):
        for index, col in self.COLUMNS.items():
            self.table.setColumnWidth(index, col.get("col_width"))

    def set_linhas(self, linhas: list[NewLancamento]):
        self.linhas = linhas
        self.load_table_data()

    def on_import_linhas(self) -> None:
        """Gera lançamentos a partir das linhas selecionadas"""
        self.import_linhas.emit(self.linhas)

    def load_lines(): 
        pass

