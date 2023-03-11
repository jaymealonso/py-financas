from PyQt5.QtCore import QObject, Qt
from PyQt5.QtWidgets import QLabel, QWidget
import util.curr_formatter as curr


class TableLine(QObject):
    @staticmethod
    def get_label_for_id(value: str):
        label = QLabel(value)
        label.setStyleSheet("color:#3f88c0")
        label.setAlignment(Qt.AlignCenter)
        return label

    @staticmethod
    def get_label_for_integer(value: int):
        label = QLabel(str(value))
        label.setAlignment(Qt.AlignCenter)
        return label

    @staticmethod
    def get_label_for_currency(value: int):
        label = QLabel(curr.int_to_locale(value))
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        TableLine.__set_gr_rd_stylesheet(value, label)
        return label

    @staticmethod
    def __set_gr_rd_stylesheet(value_int: int, source: QWidget):
        default_stylesheet = "border: none; margin-right:3px; margin-left:3px"
        if value_int < 0:
            source.setStyleSheet(f"{default_stylesheet}; color: red")
        else:
            source.setStyleSheet(f"{default_stylesheet}; color: darkgreen")
