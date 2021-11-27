import locale
import typing
from PyQt5.QtCore import Qt, QLocale, QRegExp
from PyQt5.QtGui import QValidator
from PyQt5.QtWidgets import QLineEdit, QTableView
import util.curr_formatter as curr


class QCurrencyLineEdit(QLineEdit):
    DEFAULT_STYLESHEET = "border: none; margin-right:3px; margin-left:3px"

    def __init__(self, parent: QTableView):
        super(QCurrencyLineEdit, self).__init__(parent)
        self.setAlignment(Qt.AlignRight)
        self.setStyleSheet(self.DEFAULT_STYLESHEET)
        self.setLocale(QLocale(QLocale.Portuguese, QLocale.Brazil))
        self.setValidator(QCurrencyValidator())

    def setText(self, a0: str) -> None:
        try:
            form_txt = curr.str_curr_to_locale(a0)
        except Exception as e:
            form_txt = ''
        super(QCurrencyLineEdit, self).setText(form_txt)
        self.setTextFormat()

    def setTextInt(self, a0: int) -> None:
        try:
            a0 = a0 / 100
            form_txt = locale.currency(val=a0, symbol=False, grouping=True)
        except:
            form_txt = ''
        self.setText(form_txt)

    def valueAsInt(self) -> int:
        return curr.str_curr_to_int(self.text())

    def setTextFormat(self):
        value_int = curr.str_curr_to_int(self.text())
        if value_int < 0:
            self.setStyleSheet(f"{self.DEFAULT_STYLESHEET}; color: red")
        else:
            self.setStyleSheet(f"{self.DEFAULT_STYLESHEET}; color: darkgreen")


class QCurrencyValidator(QValidator):
    def validate(self, text_to_validate: str, new_char_index: int) -> typing.Tuple['QValidator.State', str, int]:
        print(f"Enter check validation a0: '{text_to_validate}', a1: '{new_char_index}'.")

        # Check if there is a char that do not belong here
        regexp = QRegExp("[\\-0-9,. ]*")
        if not regexp.exactMatch(text_to_validate):
            print(f"VALIDATED text: '{text_to_validate}', new char index: '{new_char_index}'. Invalid")
            return QValidator.Invalid, text_to_validate, new_char_index

        # Check number format
        regexp = QRegExp("^-?(\\d{1,3}(\\.\\d{1,3})*|(\\d+))*(\\,)?(\\d*)?$")
        if not regexp.exactMatch(text_to_validate):
            print(f"VALIDATED NOT OK = text: '{text_to_validate}', new char index: '{new_char_index}'. Intermediateinv ")
            try:
                text_to_validate = curr.str_curr_to_locale(text_to_validate)
                return QValidator.Acceptable, text_to_validate, new_char_index
            except:
                return QValidator.Invalid, text_to_validate, new_char_index
        else:
            print(f"VALIDATED OK = text: '{text_to_validate}', new char index: '{new_char_index}'. Acceptable")
            try:
                text_to_validate = curr.str_curr_to_locale(text_to_validate)
            except:
                pass
            return QValidator.Acceptable, text_to_validate, new_char_index