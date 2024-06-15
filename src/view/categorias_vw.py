from unidecode import unidecode
from lib.Categoria.Table import CategoriaTableView
from lib.Genericos.MySortFilterProxyModel import MySortFilterProxyModel
from lib.Genericos.log import logging
from view.TableLine import TableLine
import view.icons.icons as icons
from enum import IntEnum, auto

from util.custom_table_delegates import ButtonDelegate, GenericInputDelegate, IDLabelDelegate
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QCursor, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (
    QPushButton,
    QWidget,
    QVBoxLayout,
    QToolBar,
    QApplication, QTableView, QMessageBox,
)
from model.Categoria import Categorias


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
        self.table: CategoriaTableView = None
        self.model_categ = Categorias()

        layout.addWidget(self.get_toolbar())
        layout.addWidget(self.get_table())

        self.setLayout(layout)

        self.load_table_data()

    def get_toolbar(self):
        self.toolbar = QToolBar()
        add_act = self.toolbar.addAction(icons.add(), "Adicionar Categoria")
        add_act.triggered.connect(self.on_add_categoria)
        self.toolbar.addSeparator()
        refresh_act = self.toolbar.addAction(icons.atualizar(), "Atualizar")
        refresh_act.triggered.connect(self.load_table_data)

        return self.toolbar

    def get_table(self) -> QTableView:
        self.table = CategoriaTableView(self)
        model = QStandardItemModel(0, len(self.COLUMNS))
        model.setHorizontalHeaderLabels([col["title"] for col in self.COLUMNS.values()])

        filter_model = MySortFilterProxyModel(self)
        filter_model.setSourceModel(model)
        self.table.setModel(filter_model)

        return self.table

    def load_model_only(self):
        self.model_categ.load()

        filter_model:MySortFilterProxyModel = self.table.model()
        model:QStandardItemModel = filter_model.sourceModel()
        model.setRowCount(len(self.model_categ.items))

        for (new_index, row) in enumerate(self.model_categ.items):

            model.setItemData( model.index(new_index, Column.ID), {Qt.UserRole: row.id}, )
            model.setItemData( model.index(new_index, Column.NM_CATEGORIA),
                {Qt.DisplayRole: row.nm_categoria, Qt.UserRole: row.nm_categoria, 
                 Qt.AccessibleTextRole: unidecode(row.nm_categoria)},
            )
            model.setItemData( model.index(new_index, Column.NR_LANCAMENTOS),
                {Qt.DisplayRole: row.tot_lancamentos, Qt.UserRole: row.tot_lancamentos},
            )

        filter_model.setSourceModel(model)
        self.table.setModel(filter_model)

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
        self.table.setItemDelegateForColumn(Column.REMOVER, ButtonDelegate(self.table, CategoriasLine.get_del_button(), 
                                     self.on_del_categoria) )

        self.table.resizeColumnToContents(0)
        self.table.setColumnWidth(Column.NM_CATEGORIA, 300)
        
        QApplication.restoreOverrideCursor()

    def on_model_item_changed(self, item: QStandardItem):
        """ Disparado pela modificação de um WIDGET na linha da tabela """
        self.table_cell_changed(item)

    def on_add_categoria(self):
        new_categoria_id = self.model_categ.add_new_empty()
        self.load_model_only()

        model = self.table.model()
        items_found = model.match(model.index(0, 0), Qt.UserRole, new_categoria_id, 1)
        item = next((x for x in items_found), None)
        if item:
            return
        self.table.scrollTo(item)
        self.table.selectRow(item.row())

    def on_del_categoria(self, index:QModelIndex):
    # def on_del_categoria(self, categoria_id: int):
        model:QStandardItemModel = index.model()
        # indexes_found = model.match(model.index(0, 0), Qt.UserRole, categoria_id, 1)
        # index = next((x for x in indexes_found), None)
        if not index:
            return
        categoria_id = model.index(index.row(), Column.ID).data(Qt.UserRole)
        categoria_descr = model.index(index.row(), Column.NM_CATEGORIA).data(Qt.UserRole)
        lancamentos_count = model.index(index.row(), Column.NR_LANCAMENTOS).data(Qt.UserRole)

        # Impede categoria 0 de ser eliminada
        if categoria_id == 0:
            QMessageBox.critical(self, "Erro", f"Não é possivel remover a categoria fixa \"{categoria_descr}\" id: \"{categoria_id}\".")
            return

        if lancamentos_count > 0:
            QMessageBox.critical(self, "Erro", f"Não é possivel remover a categoria \"{categoria_descr}\" com {lancamentos_count} lançamentos associados.")
            return

        button = QMessageBox.question(
            self,
            "Remove Lancamento?",
            f"Deseja remover a categoria \"{categoria_descr}\" id:\"{categoria_id}\" ?",
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
    def get_del_button() -> QPushButton:
        del_pbutt = QPushButton()
        del_pbutt.setToolTip("Eliminar categoria")
        del_pbutt.setIcon(icons.delete())
        return del_pbutt


class NmCategoriaInputDelegate(GenericInputDelegate):
    def createEditor(self, parent, option, index:QModelIndex):
        model = index.model()
        index_id = model.index(index.row(), Column.ID)
        categoria_id = model.data(index_id, Qt.UserRole)
        if categoria_id == 0:
            return None
        else:
            return super(NmCategoriaInputDelegate, self).createEditor(parent, option, index)





