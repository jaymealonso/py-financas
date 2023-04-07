import datetime
import locale
import logging
import util.curr_formatter as curr
from PyQt5.QtCore import Qt, QModelIndex, pyqtSignal, QStringListModel
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QWidget,
    QComboBox,
    QApplication,
    QStyle,
    QTableView,
    QDateEdit,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QCompleter,
)
from util.currency_editor import QCurrencyLineEdit

locale.setlocale(locale.LC_ALL, "pt_BR.utf8")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


class EmitterItemDelegade(QStyledItemDelegate):
    changed = pyqtSignal(QModelIndex, QWidget)


class GenericInputDelegate(EmitterItemDelegade):
    def setModelData(self, editor: QWidget, model, index: QModelIndex):
        text = editor.text()
        model.setData(index, text, Qt.DisplayRole)
        model.setData(index, text, Qt.UserRole)
        logging.debug(f"setModelData {index.row()}/{index.column()}")
        self.changed.emit(index, editor)


class CurrencyEditDelegate(EmitterItemDelegade):
    def __init__(self, parent_table: QTableView):
        super(CurrencyEditDelegate, self).__init__(parent_table)
        self.parent_table = parent_table
        logging.debug("Initialize Currency Edit")

    def createEditor(self, widget, option, index):
        logging.debug(
            f"Create Currency Editor, row: {index.row()}, col: {index.column()}"
        )
        model = self.parent_table.model()
        value = model.itemData(index)[Qt.UserRole]
        curr_edit = QCurrencyLineEdit(self.parent_table, value)
        return curr_edit

    def setEditorData(self, editor: QCurrencyLineEdit, index):
        model = self.parent_table.model()
        value: float = model.itemData(index)[Qt.UserRole] / 100
        editor.setText(locale.currency(val=value, symbol=False, grouping=False))
        logging.debug(f"setEditorData {index.row()}/{index.column()} = ???")

    def setModelData(self, editor: QCurrencyLineEdit, model, index):
        logging.debug(
            f"Before setModelData {index.row()}/{index.column()} = int {editor.text()}"
        )
        value_int: int = editor.valueAsInt()
        value_str: str = curr.str_curr_to_locale(value_int)
        model.setData(index, value_int, Qt.UserRole)
        model.setData(index, value_str, Qt.DisplayRole)

        logging.debug(
            f"After setModelData {index.row()}/{index.column()} = int {editor.text()}"
        )
        self.changed.emit(index, editor)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def paint(self, painter, option: QStyleOptionViewItem, index: QModelIndex):
        text = ""
        value = 0
        try:
            item_data = self.parent_table.model().itemData(index)
            value = item_data[Qt.UserRole]
            text = item_data[Qt.DisplayRole]
        except Exception as e:
            logging.error(f"Exception {e}")

        painter.save()
        if value < 0:
            painter.setPen(QColor(Qt.red))
        else:
            painter.setPen(QColor(Qt.darkGreen))
        option.rect.setWidth(option.rect.width() - 3)
        option.rect.center()

        painter.drawText(option.rect, Qt.AlignRight + Qt.AlignVCenter, str(text))
        painter.restore()


class ComboBoxDelegate(EmitterItemDelegade):
    def __init__(self, values: dict, parent_table: QTableView):
        super(ComboBoxDelegate, self).__init__(parent_table)

        self.parent_table = parent_table
        self.key_values = values

    def createEditor(self, widget, option, index):
        """Cria editor widget e retorna ele"""
        logging.debug(f"Create editor, row: {index.row()}, col: {index.column()}")
        # editor = ComboBoxWithSearch(
        #     self.parent_table, [x for x in self.key_values.values()]
        # )
        editor = ComboBoxWithSearch(self.parent_table, self.key_values.values())
        editor.activated.connect(self.commitAndCloseEditor)
        # for key in self.key_values:
        #     editor.addItem(self.key_values[key], key)
        return editor

    def commitAndCloseEditor(self):
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor, QStyledItemDelegate.NoHint)

    def setEditorData(self, editor: QComboBox, index):
        """Envia dados para o widget quando aberto"""
        # model = self.parent_table.model()
        # tipo_id = model.itemData(index)[Qt.UserRole]
        # value = editor.findData(tipo_id)
        # logging.debug(f"Definindo dados do Editor tipo_id: {tipo_id}, value: {value}")
        # if value:
        #     editor.setCurrentIndex(int(value))
        editor.setEditText("")
        editor.showPopup()

    def setModelData(self, editor, model, index):
        """Na finalização envia os dados de volta para o modelo"""
        tipo_id = editor.findText(editor.lineEdit().text())
        if tipo_id is None or tipo_id == -1:
            logging.debug("tipo_id vazio!")
            return
        model.setData(index, tipo_id, Qt.UserRole)
        model.setData(index, self.key_values[tipo_id], Qt.DisplayRole)
        logging.debug("setModelData")
        self.changed.emit(index, editor)


class ComboBoxWithSearch(QComboBox):
    def __init__(self, parent: QWidget, items: list[str]):
        super().__init__(parent)
        self.items = items
        self.addItems(self.items)

        self.setEditable(True)

        model = QStringListModel(self.items)
        self.setModel(model)
        self.completer = QCompleter(self.model(), self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompleter(self.completer)


class DateEditDelegate(EmitterItemDelegade):
    def __init__(self, parent_table: QTableView):
        super(DateEditDelegate, self).__init__(parent_table)
        self.parent_table = parent_table
        self.model = parent_table.model()
        logging.debug("Initialize Date Edit")

    def createEditor(self, widget, option, index: QModelIndex):
        try:
            value = self.model.itemData(index)[Qt.UserRole]
        except Exception as e:
            logging.debug(f"sem data, erro: {e}")
            value = datetime.date.today()
        date_edit = QDateEdit(self.parent_table)
        date_edit.setCalendarPopup(True)
        date_edit.setDate(value)
        return date_edit

    def setEditorData(self, editor: QDateEdit, index: QModelIndex):
        date = self.model.itemData(index)[Qt.UserRole]

        editor.setDate(date)
        editor.setCalendarPopup(True)
        logging.debug(f"setEditorData {index.row()}/{index.column()}")

    def setModelData(self, editor: QDateEdit, model, index: QModelIndex):
        date = editor.date().toPyDate()
        model.setData(index, date.strftime("%x"), Qt.DisplayRole)
        model.setData(index, date, Qt.UserRole)
        logging.debug(f"setModelData {index.row()}/{index.column()}")
        self.changed.emit(index, editor)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def paint(self, painter, option, index):
        text = ""
        try:
            text = self.model.itemData(index)[Qt.DisplayRole]
        except Exception as e:
            logging.error(f"Exception {e}")

        if isinstance(text, datetime.date):
            text = text.strftime("%x")
        option.text = text
        QApplication.style().drawControl(QStyle.CE_ItemViewItem, option, painter)
