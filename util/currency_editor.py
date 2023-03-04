import locale
import logging
import typing
import util.curr_formatter as curr
from PyQt5.QtCore import Qt, QLocale, QRegExp, QObject, QEvent
from PyQt5.QtGui import QValidator, QKeyEvent, QKeySequence
from PyQt5.QtWidgets import QLineEdit, QTableView

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] >>> %(message)s",
    handlers=[logging.StreamHandler()],
)


class QCurrencyLineEdit(QLineEdit):
    DEFAULT_STYLESHEET = "border: none; margin-right:3px; margin-left:3px"

    def __init__(self, parent: QTableView, value_int: int = 0):
        super(QCurrencyLineEdit, self).__init__(parent)
        self.setAlignment(Qt.AlignRight)
        self.setStyleSheet(self.DEFAULT_STYLESHEET)
        self.setLocale(QLocale(QLocale.Portuguese, QLocale.Brazil))

        self.installEventFilter(self)
        self.setTextInt(value_int)
        self.setValidator(QCurrencyValidator())

    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.KeyPress:
            try:
                qlineedit: QLineEdit = source
            except:
                return super(QCurrencyLineEdit, self).eventFilter(source, event)

            key_event: QKeyEvent = event
            # Modifica valor para negativo / positivo
            if key_event.key() == Qt.Key_Minus:
                pos = qlineedit.cursorPosition()
                if qlineedit.text()[0] == "-":
                    new_text = qlineedit.text()[1:]
                    logging.debug(f"KeyPress MINUS > Remove (-) new -> {new_text}")
                    pos -= 1
                else:
                    new_text = "-" + qlineedit.text()
                    pos += 1
                    logging.debug(f"KeyPress MINUS > Adding (-) new -> {new_text}")
                qlineedit.setText(new_text)
                qlineedit.setCursorPosition(pos)
                return True

            # Posiciona cursor depois do separdor de milhar
            if key_event.key() == Qt.Key_Comma:
                pos = qlineedit.text().find(",")
                if pos == -1:
                    return super(QCurrencyLineEdit, self).eventFilter(source, event)
                qlineedit.setCursorPosition(pos + 1)
                logging.debug(f"KeyPress COMMA")
                return True
            if key_event.key() == Qt.Key_Period:
                pos = qlineedit.text().find(",")
                if pos == -1:
                    return super(QCurrencyLineEdit, self).eventFilter(source, event)
                qlineedit.setCursorPosition(pos + 1)
                logging.debug(f"KeyPress PERIOD")
                return True

            # if key_event.key() == Qt.Key_Delete:
            #     if not qlineedit.selectedText():
            #         pos = qlineedit.cursorPosition()
            #         try:
            #             if qlineedit.text()[pos] == "." or qlineedit.text()[pos] == ",":
            #                 new_text = qlineedit.text()[:pos + 1] + qlineedit.text()[pos + 2:]
            #                 qlineedit.setText(new_text)
            #                 qlineedit.setCursorPosition(pos)
            #                 logging.debug(f"KeyPress DELETE")
            #                 return True
            #         except Exception as e:
            #             print(f"Exception: {e}")
            #             pass

            if Qt.Key_0 <= key_event.key() <= Qt.Key_9:
                pos = qlineedit.cursorPosition()
                if pos == 0:
                    if len(qlineedit.text()) > 0 and qlineedit.text()[pos] == "-":
                        return True

            #     try:
            #         if qlineedit.text()[pos] == "." or qlineedit.text()[pos] == ",":
            #             pass
            #         else:
            #             new_text = qlineedit.text()[:pos] + QKeySequence(event.key()).toString() + qlineedit.text()[pos + 1:]
            #             qlineedit.setText(new_text)
            #             qlineedit.setCursorPosition(pos+1)
            #             logging.debug(f"KeyPress NUMBER after dot or comma,")
            #             return True
            #     except Exception as e:
            #         print(f"Exception: {e}")
            #         return True

        return super(QCurrencyLineEdit, self).eventFilter(source, event)

    # def setText(self, a0: str) -> None:
    #     try:
    #         form_txt = curr.str_curr_to_locale(a0)
    #     except Exception as e:
    #         form_txt = ''
    #     super(QCurrencyLineEdit, self).setText(form_txt)
    #     self.setTextFormat()

    def setTextInt(self, value_int: int) -> None:
        try:
            value_float: float = value_int / 100
            form_txt = locale.currency(val=value_float, symbol=False, grouping=True)
        except:
            form_txt = ""
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
    def validate(
        self, text_to_validate: str, new_char_index: int
    ) -> typing.Tuple["QValidator.State", str, int]:
        logging.debug(
            f"Enter check validation a0: '{text_to_validate}', a1: '{new_char_index}'."
        )

        if text_to_validate == "":
            return QValidator.Acceptable, text_to_validate, new_char_index

        # Check if there is a char that do not belong here
        regexp = QRegExp("[\\-0-9,]*")
        if not regexp.exactMatch(text_to_validate):
            logging.debug(
                f"VALIDATED text: '{text_to_validate}', new char index: '{new_char_index}'. Invalid"
            )
            return QValidator.Invalid, text_to_validate, new_char_index

        return QValidator.Acceptable, text_to_validate, new_char_index

        # # Check number format
        # regexp = QRegExp("^-?(\\d{1,3}(\\.\\d{1,3})*|(\\d+))*(\\,)?(\\d*)?$")
        # if not regexp.exactMatch(text_to_validate):
        #     logging.debug(
        #         f"VALIDATED NOT OK = text: '{text_to_validate}', new char index: '{new_char_index}'. Intermediateinv ")
        #     # try:
        #     #     text_to_validate = curr.str_curr_to_locale(text_to_validate)
        #     #     return QValidator.Acceptable, text_to_validate, new_char_index
        #     # except:
        #     return QValidator.Invalid, text_to_validate, new_char_index
        # else:
        #     logging.debug(f"VALIDATED OK = text: '{text_to_validate}', new char index: '{new_char_index}'. Acceptable")
        #     # try:
        #     #     # if len(text_to_validate) == 1:
        #     #     #     text_to_validate = f"{text_to_validate}00"
        #     #     text_to_validate = curr.str_curr_to_locale(text_to_validate)
        #     # except:
        #     #     pass
        #     return QValidator.Acceptable, text_to_validate, new_char_index

    # def fixup(self, string_value: str) -> str:
    #     logging.debug("Fixup Called!")
    #     return curr.str_curr_to_locale(string_value)
