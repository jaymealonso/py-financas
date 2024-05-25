from view.TableLine import TableLine
from PyQt5.QtWidgets import QLineEdit

class VisaoGeralViewLine(TableLine):
    def get_label_for_currency(self, value: int):
        label = super().get_label_for_currency(value)
        return label

    def get_label_for_total(self, value: int):
        label = super().get_label_for_currency(value)
        label.setStyleSheet(f"{label.styleSheet()}; font-weight: bold")
        return label

    def get_label_for_total_text(self, value: str):
        label = QLineEdit(value)
        label.setReadOnly(True)
        label.setFocusPolicy(Qt.NoFocus)
        label.setStyleSheet("font-weight: bold")
        return label