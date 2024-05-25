from lib.Genericos.log import logging

from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTableView, QWidget

class VisaoGeralTableView(QTableView):
    on_selection_released = pyqtSignal(list)

    def __init__(self, parent: QWidget | None = ...) -> None:
        super().__init__(parent)
        self.setSortingEnabled(True)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        super(VisaoGeralTableView, self).mouseReleaseEvent(event)
        logging.debug("mouse release")
        self.on_mouse_release()

    def set_labels(self, header, categorias):
        self.header_labels = header
        self.categorias_labels = categorias

    def on_mouse_release(self):
        selected = self.selectedIndexes()
        logging.debug(f"{ len(selected) } cells selected.")
        filters = []
        for index, item in enumerate(selected):
            try:
                mes_ano = self.header_labels[item.column()]
                categoria_nm = self.categorias_labels[item.row()] 
            except Exception as e:
                logging.error(f"Mes/Categoria não encontrado, ind: { index }.")
                continue

            filters.append([mes_ano, categoria_nm])

        self.on_selection_released.emit(filters)