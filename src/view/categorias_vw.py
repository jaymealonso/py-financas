import logging
import view.icons.icons as icons
from enum import IntEnum, auto
from view.TableLine import TableLine
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QToolBar,
    QTableWidget,
    QTableWidgetItem,
    QApplication,
)
from model.Categoria import Categorias
import operator

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


class Column(IntEnum):
    ID = 0
    NM_CATEGORIA = auto()
    NR_LANCAMENTOS = auto()


class CategoriasView(QWidget):
    COLUMNS = {
        Column.ID: {"title": "ID", "sql_colname": "_id"},
        Column.NM_CATEGORIA: {"title": "Categoria", "sql_colname": "nm_categoria"},
        Column.NR_LANCAMENTOS: {
            "title": "Lançamentos",
            "sql_colname": "tot_lancamentos",
        },
    }

    def __init__(self):
        super(CategoriasView, self).__init__()

        layout = QVBoxLayout()

        self.toolbar: QToolBar = None
        self.table: QTableWidget = None
        self.model_categ = Categorias()

        layout.addWidget(self.get_toolbar())
        layout.addWidget(self.get_table())

        self.setLayout(layout)

    def get_toolbar(self):
        self.toolbar = QToolBar()
        add_act = self.toolbar.addAction(icons.add(), "Adicionar Categoria")
        add_act.triggered.connect(lambda: self.on_add_categoria())
        self.toolbar.addSeparator()
        refresh_act = self.toolbar.addAction(icons.atualizar(), "Atualizar")
        refresh_act.triggered.connect(lambda: self.load_table_data())

        return self.toolbar

    def get_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.COLUMNS))
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalHeaderLabels(
            [col["title"] for col in self.COLUMNS.values()]
        )
        self.load_table_data()

        return self.table

    def load_table_data(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        try:
            logging.debug("> Disconnecting table cellChanged... ")
            self.table.cellChanged.disconnect()
            logging.debug("Disconnected!")
        except Exception as e:
            logging.error(f"Cellchanged not connected! {e}")

        logging.info("Loading categorias data...")
        self.model_categ.load()

        # Limpa a tabela
        self.table.setRowCount(0)

        line = CategoriasLine()

        for row in sorted(
            self.model_categ.items, key=operator.attrgetter("nm_categoria")
        ):
            new_index = self.table.rowCount()
            self.table.insertRow(new_index)

            self.table.setCellWidget(
                new_index, Column.ID, line.get_label_for_id(str(row.id))
            )
            self.table.setItem(
                new_index, Column.NM_CATEGORIA, QTableWidgetItem(row.nm_categoria)
            )

            widget = QTableWidgetItem(str(row.tot_lancamentos))
            widget.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            widget.setFlags(widget.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(new_index, Column.NR_LANCAMENTOS, widget)

        self.table.resizeColumnToContents(0)
        self.table.setColumnWidth(1, 300)

        self.table.cellChanged.connect(self.table_cell_changed)
        logging.info("> Cellchanged connected again!")
        QApplication.restoreOverrideCursor()

    def on_add_categoria(self):
        self.model_categ.add_new_empty()
        self.load_table_data()

    def table_cell_changed(self, row: int, col: int):
        categ_dc = self.model_categ.items[row]
        item = self.table.item(row, col)
        column_data = self.COLUMNS.get(col)

        logging.info(
            f"Modificando categoria numero:{categ_dc.id}",
            f"campo \"{column_data['sql_colname']}\" para valor \"{item.text()}\"",
        )

        # categ_dc.__setattr__(column_data["sql_colname"], item.text())
        self.model_categ.update(categ_dc.id, column_data["sql_colname"], item.text())
        self.load_table_data()


class CategoriasLine(TableLine):
    def nada(self):
        pass
