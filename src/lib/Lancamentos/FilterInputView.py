from lib.Lancamentos.SortFilterProxy import LancamentoSortFilterProxyModel
from enum import StrEnum
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLineEdit, QPushButton, QTableView, QWidget
from view.icons import icons


class TEXTS(StrEnum):
    FILTRO = "Filtro"
    FILTRAR = "Filtrar"
    FILTER_BUTTON_TOOLTIP = "Filtra"
    CANCEL_BUTTON_TOOLTIP = "Limpar filtro"


class FilterInputView(QWidget):
    # sender: QDialog
    on_close_signal = pyqtSignal(QDialog)

    def __init__(self, parent) -> None:
        super(FilterInputView, self).__init__(parent)

        # vars
        self.table: QTableView = parent.table

        # layout
        layout = QHBoxLayout()
        components = ColumnSearchViewComponents(self)
        self.filter_field = components.get_filter_field()
        self.filter_button = components.get_filter_button()
        self.cancel = components.get_cancel_button()

        layout.addWidget(self.filter_field)
        layout.addWidget(self.filter_button)
        layout.addWidget(self.cancel)

        self.setLayout(layout)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Return:
            self.filter_button.click()
        elif event.key() == Qt.Key_Escape:
            self.on_fechar_popup()

    def show(self) -> None:
        super(FilterInputView, self).show()
        self.activateWindow()
        self.filter_field.setFocus()

    def on_click_filter(self):
        model: LancamentoSortFilterProxyModel = self.table.model()
        model.filter_text(self.filter_field.text())
        model.invalidateFilter()

    def on_fechar_popup(self):
        self.on_close_signal.emit(self)
        self.parent().layout().removeWidget(self)
        self.deleteLater()
        self.table.setFocus()


class ColumnSearchViewComponents:
    def __init__(self, parent: FilterInputView):
        super(ColumnSearchViewComponents, self).__init__()
        self.parent = parent

    def get_filter_button(self) -> QPushButton:
        search_button = QPushButton(TEXTS.FILTRAR)
        search_button.setIcon(icons.tab_search())
        search_button.setToolTip(TEXTS.FILTER_BUTTON_TOOLTIP)
        search_button.clicked.connect(self.parent.on_click_filter)
        return search_button

    def get_cancel_button(self) -> QPushButton:
        cancel = QPushButton()
        cancel.setIcon(icons.cancel())
        cancel.setToolTip(TEXTS.CANCEL_BUTTON_TOOLTIP)
        cancel.clicked.connect(self.parent.on_fechar_popup)
        return cancel

    def get_filter_field(self) -> QLineEdit:
        # TODO: melhorar este line edit
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(TEXTS.FILTRO)
        return line_edit
