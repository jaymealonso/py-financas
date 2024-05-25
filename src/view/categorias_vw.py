from lib.Genericos.log import logging
import view.icons.icons as icons
from enum import IntEnum, auto

from util.custom_table_delegates import GenericInputDelegate, IDLabelDelegate
from view.TableLine import TableLine
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QCursor, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QToolBar,
    QApplication, QTableView, QPushButton, QMessageBox,
)
from model.Categoria import Categorias
import operator


class Column(IntEnum):
    ID = 0
    NM_CATEGORIA = auto()
    NR_LANCAMENTOS = auto()
    REMOVER = auto()


class CategoriasView(QWidget):
    COLUMNS = {
        Column.ID: {"title": "ID", "sql_colname": "_id"},
        Column.NM_CATEGORIA: {"title": "Categoria", "sql_colname": "nm_categoria"},
        Column.NR_LANCAMENTOS: {
            "title": "Lançamentos",
            "sql_colname": "tot_lancamentos",
        },
        Column.REMOVER: {"title": "Remover"},
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

        self.load_table_data()

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

        return self.table

    def load_model_only(self):
        self.model_categ.load()

        model = self.table.model()
        model.setRowCount(len(self.model_categ.items))

        line = CategoriasLine()
        sorted_items = sorted(self.model_categ.items, key=operator.attrgetter("nm_categoria"))

        for (new_index, row) in enumerate(sorted_items):

            model.setItemData( model.index(new_index, Column.ID), {Qt.UserRole: row.id}, )
            model.setItemData( model.index(new_index, Column.NM_CATEGORIA),
                {Qt.DisplayRole: row.nm_categoria, Qt.UserRole: row.nm_categoria},
            )
            model.setItemData( model.index(new_index, Column.NR_LANCAMENTOS),
                {Qt.DisplayRole: row.tot_lancamentos, Qt.UserRole: row.tot_lancamentos},
            )

            self.table.setIndexWidget(
                model.index(new_index, Column.REMOVER),
                line.get_del_button(self, row.id),
            )

        self.table.setModel(model)

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

        self.load_model_only()

        col2_del = NmCategoriaInputDelegate(self.table)
        col2_del.changed.connect(self.on_model_item_changed)

        self.table.setItemDelegateForColumn(Column.ID, IDLabelDelegate(self.table))
        self.table.setItemDelegateForColumn(Column.NM_CATEGORIA, col2_del)
        self.table.setItemDelegateForColumn(Column.NR_LANCAMENTOS, IDLabelDelegate(self.table))

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
        new_categoria_id = self.model_categ.add_new_empty()
        self.load_model_only()

        model = self.table.model()
        items_found = model.match(model.index(0, 0), Qt.UserRole, new_categoria_id, 1)
        self.table.scrollTo(items_found[0])
        self.table.selectRow(items_found[0].row())

    def on_del_categoria(self, categoria_id: int):
        model = self.table.model()
        items_found = model.match(model.index(0, 0), Qt.UserRole, categoria_id, 1)
        if len(items_found) == 0:
            return
        item_found = items_found[0]
        categoria_descr = model.item(item_found.row(), Column.NM_CATEGORIA).data(Qt.UserRole)
        nr_lancamentos = model.item(item_found.row(), Column.NR_LANCAMENTOS).data(Qt.UserRole)
        if nr_lancamentos != 0:
            QMessageBox.critical(self, "Erro", "Não é possivel remover uma categoria com lançamentos associados.")
            return

        button = QMessageBox.question(
            self,
            "Remove Lancamento?",
            f"Deseja remover a categoria {categoria_descr}({categoria_id}) ?",
            buttons=QMessageBox.Yes | QMessageBox.No,
            defaultButton=QMessageBox.No,
        )
        if button == QMessageBox.No:
            return

        logging.debug(f"Eliminando categoria {categoria_id} do banco de dados ...")
        self.model_categ.delete(categoria_id)

        self.load_model_only()

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
    @staticmethod
    def get_del_button(parent: CategoriasView, categoria_id: int):
        del_pbutt = QPushButton()
        del_pbutt.setEnabled(categoria_id != 0)
        del_pbutt.setToolTip("Eliminar categoria")
        del_pbutt.setIcon(icons.delete())
        del_pbutt.clicked.connect(lambda: parent.on_del_categoria(categoria_id))
        return del_pbutt


class NmCategoriaInputDelegate(GenericInputDelegate):
    def createEditor(self, parent, option, index):
        model = self.parent().model()
        categoria_id = model.item(index.row(), Column.ID).data(Qt.UserRole)
        if categoria_id == 0:
            return None
        else:
            return super(NmCategoriaInputDelegate, self).createEditor(parent, option, index)





