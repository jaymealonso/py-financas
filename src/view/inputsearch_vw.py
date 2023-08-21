from enum import StrEnum
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt, QModelIndex, pyqtSignal
from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QWidget, QHBoxLayout, QTableView, QLabel
from view.icons import icons


class TEXTS(StrEnum):
    NADA_ENCONTRADO = 'Nada encontrado.'
    PROCURAR = 'Procurar'
    SEARCH_BUTTON_TOOLTIP = 'Executa procura'
    CANCEL_BUTTON_TOOLTIP = 'Ocultar busca'
    FOUND_MATCHES = "{0} de {1}"
    SEARCHING_IN_THE_COLUMN = "Procurando na coluna \"{0}\""
    NEXT_RESULT = 'Próximo resultado.'
    PREV_RESULT = 'Resultado anterior.'


class ColumnSearchView(QWidget):
    # sender: QDialog
    on_close_signal = pyqtSignal(QDialog)

    def __init__(self, parent: QWidget):
        super(ColumnSearchView, self).__init__(parent)

        self.column_index: int = -1
        self.last_found_string: str = None
        self.found_matches: list[QModelIndex] = []
        self.found_matches_index: int = -1

        layout = QHBoxLayout()
        components = ColumnSearchViewComponents(self)
        self.search_field = components.get_search_field()
        self.found_matches_label = QLabel(TEXTS.NADA_ENCONTRADO)
        self.search_button = components.get_search_button()
        self.prev_button = components.get_prev_button()
        self.next_button = components.get_next_button()
        self.cancel = components.get_cancel_button()

        layout.addWidget(self.search_field)
        layout.addWidget(self.found_matches_label)
        layout.addWidget(self.prev_button)
        layout.addWidget(self.next_button)
        layout.addWidget(self.search_button)
        layout.addWidget(self.cancel)
        self.setLayout(layout)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Return:
            self.search_button.click()
        elif event.key() == Qt.Key_Escape:
            self.on_close_signal.emit(self)
            self.parent().layout().removeWidget(self)
            self.deleteLater()

    def show2(self, column_name: str, column_index: int) -> None:
        if self.column_index != column_index:
            self.setWindowTitle(TEXTS.SEARCHING_IN_THE_COLUMN.format(column_name))
            self.found_matches_label.setText(TEXTS.NADA_ENCONTRADO)
            self.search_field.clear()
            self.search_field.setPlaceholderText(column_name)
            self.column_index = column_index

        super(ColumnSearchView, self).show()
        self.activateWindow()
        self.search_field.setFocus()

    def on_click_search(self, go_prev=False):
        table: QTableView = self.parent().table
        model = table.model()

        select_indexes = table.selectedIndexes()
        from_line = select_indexes[0].row() if len(select_indexes) > 0 else 1

        if self.last_found_string == self.search_field.text() and len(self.found_matches) > 0:
            self.found_matches_index += (-1 if go_prev else 1)
            if self.found_matches_index > len(self.found_matches) - 1:
                self.found_matches_index = 0
            if self.found_matches_index < 0:
                self.found_matches_index = len(self.found_matches) - 1
            set_index = self.found_matches[self.found_matches_index]
        else:
            self.found_matches = []
            if self.search_field.text() != "":
                self.found_matches = model.match(
                    model.index(from_line, self.column_index),
                    Qt.DisplayRole,
                    self.search_field.text(),
                    -1,
                    Qt.MatchContains | Qt.MatchWrap
                )
            if len(self.found_matches) == 0:
                self.found_matches_label.setText(TEXTS.NADA_ENCONTRADO)
                return
            set_index = self.found_matches[0]
            self.found_matches_index = 0

        table.setCurrentIndex(set_index)
        self.found_matches_label.setText(
            TEXTS.FOUND_MATCHES.format(self.found_matches_index + 1, len(self.found_matches))
        )
        self.last_found_string = self.search_field.text()

    def on_cancel(self):
        self.on_close_signal.emit(self)
        self.parent().layout().removeWidget(self)
        self.deleteLater()


class ColumnSearchViewComponents:
    def __init__(self, parent: ColumnSearchView):
        super(ColumnSearchViewComponents, self).__init__()
        self.parent = parent

    def get_search_button(self) -> QPushButton:
        search_button = QPushButton(TEXTS.PROCURAR)
        search_button.setIcon(icons.tab_search())
        search_button.setToolTip(TEXTS.SEARCH_BUTTON_TOOLTIP)
        search_button.clicked.connect(lambda: self.parent.on_click_search())
        return search_button

    def get_cancel_button(self) -> QPushButton:
        cancel = QPushButton()
        cancel.setIcon(icons.cancel())
        cancel.setToolTip(TEXTS.CANCEL_BUTTON_TOOLTIP)
        cancel.clicked.connect(lambda: self.parent.on_cancel())
        return cancel

    def get_search_field(self) -> QLineEdit:
        # TODO: melhorar este line edit
        return QLineEdit()

    def get_prev_button(self):
        cancel = QPushButton()
        cancel.setIcon(icons.results_prev())
        cancel.setToolTip(TEXTS.PREV_RESULT)
        cancel.clicked.connect(lambda: self.parent.on_click_search(go_prev=True))
        return cancel

    def get_next_button(self):
        cancel = QPushButton()
        cancel.setIcon(icons.results_next())
        cancel.setToolTip(TEXTS.NEXT_RESULT)
        cancel.clicked.connect(lambda: self.parent.on_click_search())
        return cancel
