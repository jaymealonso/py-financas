import logging
from enum import StrEnum

from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QWidget, QHBoxLayout, QTableView, QBoxLayout, QLabel


class TEXTS(StrEnum):
    NADA_ENCONTRADO = 'Nada encontrado.'
    PROCURAR = 'Procurar'


class ColumnSearchView(QDialog):
    def __init__(self, parent: QWidget):
        super(ColumnSearchView, self).__init__(parent)

        self.column_index: int = -1
        self.last_found_string: str = None
        self.found_matches: list[QModelIndex] = []
        self.found_matches_index: int = -1

        layout = QHBoxLayout()
        self.search_field = QLineEdit()
        self.found_matches_label = QLabel(TEXTS.NADA_ENCONTRADO)
        self.search_button = QPushButton(TEXTS.PROCURAR)
        self.search_button.clicked.connect(lambda: self.on_click_search())

        layout.addWidget(self.search_field)
        layout.addWidget(self.found_matches_label)
        layout.addWidget(self.search_button)

        self.setMinimumSize(500, 78)
        self.setLayout(layout)

    def show2(self, column_name: str, column_index: int) -> None:
        self.setWindowTitle(f"Procurando na coluna \"{column_name}\"")
        self.column_index = column_index

        super(ColumnSearchView, self).show()

    def on_click_search(self):
        table: QTableView = self.parent().table
        model = table.model()

        from_line = table.selectedIndexes()[0].row() + 1

        if self.last_found_string == self.search_field.text() and len(self.found_matches) > 0:
            # find next in self.found_matches
            self.found_matches_index += 1
            if self.found_matches_index > len(self.found_matches) - 1:
                self.found_matches_index = 0
            set_index = self.found_matches[self.found_matches_index]
        else:
            self.found_matches = model.match(
                model.index(from_line, self.column_index),
                Qt.DisplayRole,
                self.search_field.text(),
                100,
                Qt.MatchContains | Qt.MatchWrap
            )
            if len(self.found_matches) == 0:
                self.found_matches_label.setText(TEXTS.NADA_ENCONTRADO)
                return
            set_index = self.found_matches[0]
            self.found_matches_index = 0

        table.setCurrentIndex(set_index)
        self.found_matches_label.setText(f"{self.found_matches_index + 1} de {len(self.found_matches)}")
        self.last_found_string = self.search_field.text()
