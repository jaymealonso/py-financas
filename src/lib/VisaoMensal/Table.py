#!

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QTableView, QWidget

from lib.Genericos.log import logging


class VisaoGeralTableView(QTableView):
    selection_released = pyqtSignal(list)

    def __init__(self, parent: QWidget | None = ...) -> None:
        super().__init__(parent)
        # vars
        self.header_labels = None
        self.categorias_labels = None

        self.setSortingEnabled(True)

    def keyPressEvent(self, e: QtGui.QKeyEvent | None) -> None:
        super().keyPressEvent(e)
        if e.key() in (Qt.Key.Key_Down, Qt.Key.Key_Up, Qt.Key.Key_Left,Qt.Key.Key_Right):
            self.on_selection_ended()


    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
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
