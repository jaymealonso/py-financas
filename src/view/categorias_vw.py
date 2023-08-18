import logging
import view.icons.icons as icons
from enum import IntEnum, auto

from util.custom_table_delegates import GenericInputDelegate
from view.TableLine import TableLine
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QCursor, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QToolBar,
    QTableWidgetItem,
    QApplication, QTableView,
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
        self.table: QTableView = None
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

    def get_table(self) -> QTableView:
        self.table = QTableView()
        model = QStandardItemModel(0, len(self.COLUMNS))
        model.setHorizontalHeaderLabels([col["title"] for col in self.COLUMNS.values()])

        self.table.setModel(model)
        self.table.verticalHeader().setVisible(False)

        # self.table.setColumnCount(len(self.COLUMNS))
        # self.table.verticalHeader().setVisible(False)
        # self.table.setHorizontalHeaderLabels(
        #     [col["title"] for col in self.COLUMNS.values()]
        # )
        self.load_table_data()

        return self.table

    def load_table_data(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        model = self.table.model()
        try:
            logging.debug("> Disconnecting table itemChanged... ")
            model.itemChanged.disconnect()
            logging.debug("Disconnected!")
        except Exception as e:
            logging.error(f"itemChanged not connected! {e}")

        logging.info("Loading categorias data...")
        self.model_categ.load()

        # Limpa a tabela
        model.setRowCount(0)

        line = CategoriasLine()

        sorted_items = sorted(self.model_categ.items, key=operator.attrgetter("nm_categoria"))
        for row in sorted_items:
            new_index = model.rowCount()
            model.insertRow(new_index)

            self.table.setIndexWidget(
                model.index(new_index, Column.ID),
                line.get_label_for_id(str(row.id)),
            )
            self.table.setIndexWidget(
                model.index(new_index, Column.NR_LANCAMENTOS),
                line.get_label_for_id(str(row.tot_lancamentos)),
            )

            model.setItemData( model.index(new_index, Column.ID), {Qt.UserRole: row.id}, )
            model.setItemData( model.index(new_index, Column.NM_CATEGORIA),
                {Qt.DisplayRole: row.nm_categoria, Qt.UserRole: row.nm_categoria},
            )
            model.setItemData( model.index(new_index, Column.NR_LANCAMENTOS),
                {Qt.DisplayRole: row.tot_lancamentos, Qt.UserRole: row.tot_lancamentos},
            )

            widget = QTableWidgetItem(str(row.tot_lancamentos))
            widget.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            widget.setFlags(widget.flags() & ~Qt.ItemIsEditable)
            # self.table.setItem(new_index, Column.NR_LANCAMENTOS, widget)

        col2_del = GenericInputDelegate(self.table)
        col2_del.changed.connect(self.on_model_item_changed)

        self.table.setItemDelegateForColumn(Column.NM_CATEGORIA, col2_del)

        self.table.resizeColumnToContents(0)
        self.table.setColumnWidth(1, 300)

        # self.table.cellChanged.connect(self.table_cell_changed)
        # logging.info("> Cellchanged connected again!")
        QApplication.restoreOverrideCursor()

    def on_model_item_changed(self, item: QStandardItem):
        """
        Disparado pela modificação de um WIDGET na linha da tabela
        """
        self.table_cell_changed(item)

    def on_add_categoria(self):
        self.model_categ.add_new_empty()
        self.load_table_data()

    def table_cell_changed(self, item: QModelIndex):
        row = item.row()
        col = item.column()

        model = self.table.model()
        categoria_id = model.data(model.index(row, Column.ID), Qt.UserRole)
        value = model.data(item, Qt.UserRole)

        column_data = self.COLUMNS.get(col)
        sql_colname = column_data["sql_colname"]

        logging.info(
            f"Modificando categoria numero:{categoria_id}",
            f"campo \"{sql_colname}\" para valor \"{value}\"",
        )

        self.model_categ.update(categoria_id, sql_colname, value)
        self.load_table_data()


class CategoriasLine(TableLine):
    pass
