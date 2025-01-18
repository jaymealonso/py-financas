from PyQt5.QtCore import QObject, Qt
from PyQt5.QtWidgets import QWidget, QLineEdit
import util.curr_formatter as curr


class TableLine(QObject):
    """Classe para criar widgets usados em várias tabelas"""

    @staticmethod
    def get_label_for_id(value: str):
        label = QLineEdit(value)
        label.setStyleSheet("color:#3f88c0")
        label.setReadOnly(True)
        label.setFocusPolicy(Qt.NoFocus)
        label.setAlignment(Qt.AlignCenter)
        return label

    @staticmethod
    def get_label_for_integer(value: int):
        label = QLineEdit(str(value))
        label.setReadOnly(True)
        label.setFocusPolicy(Qt.NoFocus)
        label.setAlignment(Qt.AlignCenter)
        return label

    @staticmethod
    def get_label_for_currency(value: int):
        label = QLineEdit(curr.int_to_locale(value))
        label.setReadOnly(True)
        label.setFocusPolicy(Qt.NoFocus)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        TableLine.__set_gr_rd_stylesheet(value, label)
        return label

    @staticmethod
    def __set_gr_rd_stylesheet(value_int: int, source: QWidget):
        default_stylesheet = ""
        if value_int < 0:
            source.setStyleSheet(f"{default_stylesheet} color: red")
        else:
            source.setStyleSheet(f"{default_stylesheet} color: darkgreen")
