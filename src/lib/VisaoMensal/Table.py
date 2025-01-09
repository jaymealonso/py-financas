#!

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QTableView, QWidget, QHeaderView

from lib.Genericos.log import logging
from util.custom_table_delegates import IDLabelDelegate


class FreezeTableWidget(QTableView):
    """Classe para congelar colunas de uma tabela. Peguei da internet não sei como funciona."""

    def __init__(self, model):
        super(FreezeTableWidget, self).__init__()
        self.frozenTableView = QTableView(self)

        # Events
        self.horizontalHeader().sectionResized.connect(self.updateSectionWidth)
        self.verticalHeader().sectionResized.connect(self.updateSectionHeight)
        self.frozenTableView.verticalScrollBar().valueChanged.connect(self.verticalScrollBar().setValue)
        self.verticalScrollBar().valueChanged.connect(self.frozenTableView.verticalScrollBar().setValue)

    def setModel(self, model):
        super().setModel(model)
        self.init()

    def init(self):
        self.frozenTableView.setModel(self.model())
        self.frozenTableView.setFocusPolicy(Qt.NoFocus)
        self.frozenTableView.verticalHeader().hide()
        self.frozenTableView.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.viewport().stackUnder(self.frozenTableView)

        # self.frozenTableView.setStyleSheet("""
        #     QTableView { border: none;
        #                  background-color: #8EDE21;
        #                  selection-background-color: #999;
        #     }""")  # for demo purposes

        self.frozenTableView.setSelectionModel(self.selectionModel())
        for col in range(1, self.model().columnCount()):
            self.frozenTableView.setColumnHidden(col, True)
        self.frozenTableView.setColumnWidth(0, self.columnWidth(0))
        self.frozenTableView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.frozenTableView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.frozenTableView.setItemDelegateForColumn(0, IDLabelDelegate(self.frozenTableView))
        self.frozenTableView.show()
        self.updateFrozenTableGeometry()
        self.setHorizontalScrollMode(self.ScrollPerPixel)
        self.setVerticalScrollMode(self.ScrollPerPixel)
        self.frozenTableView.setVerticalScrollMode(self.ScrollPerPixel)

    def updateSectionWidth(self, logicalIndex, oldSize, newSize):
        if logicalIndex == 0:
            self.frozenTableView.setColumnWidth(0, newSize)
            self.updateFrozenTableGeometry()

    def updateSectionHeight(self, logicalIndex, oldSize, newSize):
        self.frozenTableView.setRowHeight(logicalIndex, newSize)

    def resizeEvent(self, event):
        super(FreezeTableWidget, self).resizeEvent(event)
        self.updateFrozenTableGeometry()

    def moveCursor(self, cursorAction, modifiers):
        current = super(FreezeTableWidget, self).moveCursor(cursorAction, modifiers)
        if (
            cursorAction == self.MoveLeft
            and self.current.column() > 0
            and self.visualRect(current).topLeft().x() < self.frozenTableView.columnWidth(0)
        ):
            newValue = (
                self.horizontalScrollBar().value()
                + self.visualRect(current).topLeft().x()
                - self.frozenTableView.columnWidth(0)
            )
            self.horizontalScrollBar().setValue(newValue)
        return current

    def scrollTo(self, index, hint):
        if index.column() > 0:
            super(FreezeTableWidget, self).scrollTo(index, hint)

    def updateFrozenTableGeometry(self):
        self.frozenTableView.setGeometry(
            self.verticalHeader().width() + self.frameWidth(),
            self.frameWidth(),
            self.columnWidth(0),
            self.viewport().height() + self.horizontalHeader().height(),
        )


class VisaoGeralTableView(FreezeTableWidget):
    """Classe para a tabela de visão geral."""

    selection_released = pyqtSignal(list)
    """Sinal emitido quando a seleção é liberada."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        # vars
        self.header_labels = None
        self.categorias_labels = None

        self.setSortingEnabled(True)

    def keyPressEvent(self, e: QtGui.QKeyEvent | None) -> None:
        super().keyPressEvent(e)
        if not e:
            return
        if (
            e.key() == Qt.Key.Key_Down
            or e.key() == Qt.Key.Key_Up
            or e.key() == Qt.Key.Key_Left
            or e.key() == Qt.Key.Key_Right
        ):
            self.on_selection_ended()

    def mouseReleaseEvent(self, event: QMouseEvent | None = None):
        super(VisaoGeralTableView, self).mouseReleaseEvent(event)
        logging.debug("mouse release")
        self.on_selection_ended()

    def set_labels(self, header, categorias):
        self.header_labels = header
        self.categorias_labels = categorias

    def on_selection_ended(self):
        selected = self.selectedIndexes()
        logging.debug(f"{ len(selected) } cells selected.")
        filters = []
        for index, item in enumerate(selected):
            try:
                mes_ano = self.header_labels[item.column()]
                categoria_nm = self.categorias_labels[item.row()]
            except Exception:
                logging.debug(f"Mes/Categoria não encontrado, ind: { index }.")
                continue

            filters.append([mes_ano, categoria_nm])

        self.selection_released.emit(filters)
