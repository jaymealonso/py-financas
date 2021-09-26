from PyQt5.QtCore import QObject, Qt
from PyQt5.QtWidgets import QLabel
import util.curr_formatter as curr


class TableLine(QObject):
    @staticmethod
    def get_label_for_id(value: str):
        label = QLabel(value)
        label.setStyleSheet("color:red")
        label.setAlignment(Qt.AlignCenter)
        return label

    @staticmethod
    def get_label_for_integer(value: int):
        label = QLabel(str(value))
        label.setAlignment(Qt.AlignCenter)
        return label

    @staticmethod
    def get_label_for_currency(value: float):
        label = QLabel(curr.float_to_locale(value))
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return label



