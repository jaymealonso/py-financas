from PyQt5.QtWidgets import QTableView, QWidget

from lib.Genericos.log import logging  # noqa: F401


class CategoriaTableView(QTableView):
    def __init__(self, parent: QWidget | None = ...) -> None:
        super(CategoriaTableView, self).__init__(parent)

        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)


