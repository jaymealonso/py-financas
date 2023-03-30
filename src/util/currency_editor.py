import locale
import logging
import typing
import util.curr_formatter as curr
from PyQt5.QtCore import Qt, QLocale, QRegExp, QObject, QEvent
from PyQt5.QtGui import QValidator, QKeyEvent
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
            except Exception as e:
                logging.info(f"erro lineedit {e}, retornando padrão...")
                return super(QCurrencyLineEdit, self).eventFilter(source, event)

            key_event: QKeyEvent = event
            # Modifica valor para negativo / positivo
            if key_event.key() == Qt.Key_Minus and qlineedit.valueAsInt() > 0:
                pos = qlineedit.cursorPosition()
                if len(qlineedit.text()) == 0:
                    return True
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
            if key_event.key() == Qt.Key_Comma or key_event.key() == Qt.Key_Period:
                pos = qlineedit.text().find(",")
                if pos == -1:
                    return super(QCurrencyLineEdit, self).eventFilter(source, event)
                qlineedit.setCursorPosition(pos + 1)
                logging.debug("KeyPress COMMA")
                return True

        return super(QCurrencyLineEdit, self).eventFilter(source, event)

    def setTextInt(self, value_int: int) -> None:
        """Define valor em inteiro que será o valor da coluna"""
        try:
            value_float: float = value_int / 100
            form_txt = locale.currency(val=value_float, symbol=False, grouping=False)
        except Exception as e:
            logging.info(f'Não consegui formatar string, retornando vazio "". {e}')
            form_txt = ""
        self.setText(form_txt)

    def valueAsInt(self) -> int:
        """Busca valor como inteiro"""
        try:
            return curr.str_curr_to_int(self.text())
        except Exception as e:
            logging.info(f"Não inteiro, retornando zero. {e}")
            return 0

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
