import locale
import datetime
import logging

from PyQt5.QtGui import QPalette, QColor

# from util.log import Logger
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox, QApplication, QStyle, QTableView, QDateEdit, QStyledItemDelegate, QLabel, \
    QPushButton, QStyleOptionViewItem
from util.currency_editor import QCurrencyLineEdit
import util.curr_formatter as curr
locale.setlocale(locale.LC_ALL, "pt_br")


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()])


class CurrencyEditDelegate(QStyledItemDelegate):
    def __init__(self, parent_table: QTableView):
        super(CurrencyEditDelegate, self).__init__(parent_table)
        # self.date = ""
        self.parent_table = parent_table
        logging.debug("Initialize Currency Edit")

    def createEditor(self, widget, option, index):
        logging.debug(f"Create Currency Editor, row: {index.row()}, col: {index.column()}")
        model = self.parent_table.model()
        value = model.itemData(index)[0]
        curr_edit = QCurrencyLineEdit(self.parent_table)
        curr_edit.setTextInt(value)
        return curr_edit

    def setEditorData(self, editor: QCurrencyLineEdit, index):
        model = self.parent_table.model()

        value_str = model.itemData(index)[0]
        editor.setText(value_str)
        logging.debug(f"setEditorData {index.row()}/{index.column()} = str {value_str}")

    def setModelData(self, editor: QCurrencyLineEdit, model, index):
        logging.debug(f"Before setModelData {index.row()}/{index.column()} = int {editor.text()}")
        model.setData(index, editor.valueAsInt(), Qt.EditRole)
        logging.debug(f"After setModelData {index.row()}/{index.column()} = int {editor.text()}")

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def paint(self, painter, option: QStyleOptionViewItem, index):
        text = ""
        value = 0
        try:
            text_str = self.parent_table.model().item(index.row(), index.column()).text()
            value = curr.str_curr_to_int(text_str)
            text = curr.str_curr_to_locale(text_str)
        except Exception as e:
            logging.error(f"Exception {e}")

        painter.save()
        if value < 0:
            painter.setPen(QColor(Qt.red))
        else:
            painter.setPen(QColor(Qt.darkGreen))
        option.rect.setWidth(option.rect.width() - 3)
        option.rect.center()

        painter.drawText(option.rect, Qt.AlignRight, text)
        painter.restore()

        # QApplication.style().drawItemText(
        #     painter, option.rect, option.displayAlignment,
        #     option.palette, True, option.text, QPalette.NoRole)
#        QApplication.style().drawControl(QStyle.CE_ItemViewItem, option, painter)


class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, values: dict, parent_table: QTableView):
        super(ComboBoxDelegate, self).__init__(parent_table)

        self.parent_table = parent_table
        self.key_values = values

    def createEditor(self, widget, option, index):
        logging.debug(f"Create editor, row: {index.row()}, col: {index.column()}")
        editor = QComboBox(widget)
        for key in self.key_values:
            editor.addItem(self.key_values[key], key)
        return editor

    def setEditorData(self, editor: QComboBox, index):
        model = self.parent_table.model()
        tipo_id = model.itemData(index)[0]
        value = editor.findData(tipo_id)
        if value:
            editor.setCurrentIndex(int(value))
        editor.showPopup()
        logging.debug("setEditorData")

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentData(), Qt.EditRole)
        logging.debug("setModelData")

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def paint(self, painter, option, index):
        text = ""
        try:
            model = self.parent_table.model()
            tipo_id = model.itemData(index)[0]
            text = self.key_values[tipo_id]
        except Exception as e:
            logging.error(f"Exception {e}")
        option.text = text
        QApplication.style().drawControl(QStyle.CE_ItemViewItem, option, painter)


class DateEditDelegate(QStyledItemDelegate):
    def __init__(self, parent_table: QTableView):
        super(DateEditDelegate, self).__init__(parent_table)
        # self.date = ""
        self.parent_table = parent_table
        logging.debug("Initialize Date Edit")

    def createEditor(self, widget, option, index):
        logging.debug(f"Create editor, row: {index.row()}, col: {index.column()}")
        model = self.parent_table.model()
        date = model.itemData(index)[0]
        try:
            value = datetime.datetime.fromisoformat(date)
        except:
            value = datetime.date.today()
        date_edit = QDateEdit(self.parent_table)
        date_edit.setCalendarPopup(True)
        date_edit.setDate(value)
        return date_edit

    def setEditorData(self, editor: QDateEdit, index):
        model = self.parent_table.model()
        date_str = model.itemData(index)[0]
        date_value = datetime.datetime.fromisoformat(date_str)
        editor.setDate(date_value)
        editor.setCalendarPopup(True)
        logging.debug(f"setEditorData {index.row()}/{index.column()}")

    def setModelData(self, editor: QDateEdit, model, index):
        model.setData(index, editor.date().toString("yyyy-MM-dd"), Qt.EditRole)
        logging.debug(f"setModelData {index.row()}/{index.column()}")

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def paint(self, painter, option, index):
        text = ""
        try:
            date_striso = self.parent_table.model().item(index.row(), index.column()).text()
            date = datetime.datetime.fromisoformat(date_striso)
            text = date.strftime('%x')
        except Exception as e:
            logging.error(f"Exception {e}")
        option.text = text
        QApplication.style().drawControl(QStyle.CE_ItemViewItem, option, painter)
