from typing import cast
from PyQt5.QtCore import QTextStream, Qt
from PyQt5.QtWidgets import QLabel

from util import int_to_locale


FieldAlignment = QTextStream.FieldAlignment
AlignmentFlag = Qt.AlignmentFlag
Alignment = Qt.Alignment


class TotalCurrLabel(QLabel):
    def set_int_value(self, value_int: int):
        self.setText(int_to_locale(value_int))
        color = "color:darkgreen"
        if value_int < 0:
            color = "color:red"
        stylesheet = f"margin-right:3px; margin-left:3px; font-weight:bold; {color}"
        self.setStyleSheet(stylesheet)
        new_alignment = cast(Alignment, AlignmentFlag.AlignRight | AlignmentFlag.AlignVCenter)
        self.setAlignment(new_alignment)
