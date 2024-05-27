from lib.Genericos.log import logging

import datetime
import locale
import util.curr_formatter as curr
from collections.abc import Callable
from PyQt5.QtCore import Qt, QModelIndex, pyqtSignal, QStringListModel
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QWidget,
    QComboBox,
    QApplication,
    QStyle,
    QTableView,
    QDateEdit,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QCompleter, QPushButton,
)
from util.currency_editor import QCurrencyLineEdit
from view.icons import icons

locale.setlocale(locale.LC_ALL, "pt_BR.utf8")


class EmitterItemDelegade(QStyledItemDelegate):
    changed = pyqtSignal(QModelIndex, QWidget)


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

    def hidePopup(self) -> None:
        logging.debug("BLOCKED *** Hide pop")
        pass


# TODO: funciona mas aparentemente ainda tem bugs no caso de scroll acontecer.
#       verificar o paint quando dá openpersistent
class ButtonDelegate(QStyledItemDelegate):
    pressed = pyqtSignal(QModelIndex, QWidget)

    def __init__(self, parent_table: QTableView, function: Callable[[int], None]):
        super(ButtonDelegate, self).__init__(parent_table)
        self.function = function
        self.parent_table = parent_table
        self.button:QPushButton = None
        # self.button.clicked.connect(function)

        logging.debug("Initialize Button")

    def createEditor(self, widget, option, index):
        button = self.get_del_button(widget)
        button.clicked.connect(lambda: self.function(self.parent_table, index))
        return button

    def setEditorData(self, editor, index):
        pass

    def setModelData(self, editor, model, index):
        pass

    def paint(self, painter, option: QStyleOptionViewItem, index: QModelIndex):
        self.parent_table.openPersistentEditor(index)

    @staticmethod
    def get_del_button(widget) -> QPushButton:
        del_pbutt = QPushButton(widget) 
        del_pbutt.setToolTip("Eliminar Lançamento")
        del_pbutt.setIcon(icons.delete())
        return del_pbutt


class IDLabelDelegate(QStyledItemDelegate):
    def __init__(self, parent_table: QTableView):
        super(IDLabelDelegate, self).__init__(parent_table)
        self.parent_table = parent_table
        logging.debug("Initialize Label")

    def createEditor(self, parent, option, index):
        pass

    def setEditorData(self, editor, index):
        pass

    def setModelData(self, editor, model, index):
        pass

    def paint(self, painter, option: QStyleOptionViewItem, index: QModelIndex):
        text = ""
        try:
            text = index.data(Qt.UserRole)
            font = (index.data(Qt.FontRole) or QFont())
        except Exception as e:
            logging.error(f"IDLabelDelegate Exception {e}")

        painter.save()
        painter.setPen(QColor(63, 136, 192))
        option.rect.setWidth(option.rect.width() - 3)
        option.rect.center()

        painter.setFont(font)
        painter.drawText(option.rect, Qt.AlignHCenter + Qt.AlignVCenter, str(text))
        painter.restore()


class CurrencyLabelDelegate(QStyledItemDelegate):
    def __init__(self, parent_table: QTableView, center: bool = False, bold: bool = False):
        super(CurrencyLabelDelegate, self).__init__(parent_table)
        self.parent_table = parent_table
        logging.debug("Initialize Label")
        self.center = center
        self.bold = bold

    def createEditor(self, parent, option, index):
        pass

    def setEditorData(self, editor, index):
        pass

    def setModelData(self, editor, model, index):
        pass

    def paint(self, painter, option: QStyleOptionViewItem, index: QModelIndex):
        text = ""
        value = 0
        try:
            value = index.data(Qt.UserRole)
            text  = index.data(Qt.DisplayRole)
            font  = index.data(Qt.FontRole) or QFont()
            if value is None or text is None or font is None:
                return
        except Exception as e:
            logging.error(f"CurrencyLabelDelegate Exception {e}")

        painter.save()
        if value < 0:
            painter.setPen(QColor(Qt.red))
        else:
            painter.setPen(QColor(Qt.darkGreen))
        option.rect.setWidth(option.rect.width() - 3)
        option.rect.center()
        if self.bold:
            font.setBold(True)

        flags = Qt.AlignVCenter + (Qt.AlignHCenter if self.center else Qt.AlignRight)
        painter.setFont(font)

        painter.drawText(option.rect, flags, str(text))
        painter.restore()


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

    def createEditor(self, widget, option, index: QModelIndex):
        logging.debug(
            f"Create Currency Editor, row: {index.row()}, col: {index.column()}"
        )
        value = index.data(Qt.UserRole)
        curr_edit = QCurrencyLineEdit(widget, value)
        return curr_edit

    def setEditorData(self, editor: QCurrencyLineEdit, index):
        value: float = index.data(Qt.UserRole) / 100
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
        try:
            value = index.data(Qt.UserRole) 
            text = index.data(Qt.DisplayRole)
        except Exception as e:
            logging.error(f"CurrencyEditDelegate Exception {e}")

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

    def createEditor(self, parent, option, index):
        """Cria editor widget e retorna ele"""
        logging.debug(f"Create editor, row: {index.row()}, col: {index.column()}")
        editor = ComboBoxWithSearch(parent, self.key_values.values())
        editor.activated.connect(self.commitAndCloseEditor)
        return editor

    def commitAndCloseEditor(self):
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor, QStyledItemDelegate.NoHint)

    def setEditorData(self, editor: QComboBox, index):
        """Envia dados para o widget quando aberto"""
        logging.debug("Combobox Clear")
        editor.clearEditText()
        logging.debug("Show popup")
        editor.showPopup()

    def setModelData(self, editor: ComboBoxWithSearch, model, index: QModelIndex):
        """Na finalização envia os dados de volta para o modelo"""
        tipo_id_combo_index = editor.findText(editor.lineEdit().text())
        if tipo_id_combo_index is None or tipo_id_combo_index == -1 or tipo_id_combo_index >= len( editor.items ):
            logging.debug(f"tipo_id vazio! index: { tipo_id_combo_index }")
            return
        tipo_id = list(self.key_values.keys())[tipo_id_combo_index]
        model.setData(index, tipo_id, Qt.UserRole)
        model.setData(index, self.key_values.get(tipo_id), Qt.DisplayRole)
        logging.debug("setModelData")
        self.changed.emit(index, editor)


class DateEditDelegate(EmitterItemDelegade):
    def __init__(self, parent_table: QTableView):
        super(DateEditDelegate, self).__init__(parent_table)
        self.parent_table = parent_table
        self.model = parent_table.model()
        logging.debug("Initialize Date Edit")

    def createEditor(self, widget, option, index: QModelIndex):
        try:
            value = index.data(Qt.UserRole) # self.model.itemData(index)[Qt.UserRole]
        except Exception as e:
            logging.debug(f"sem data, erro: {e}")
            value = datetime.date.today()
        date_edit = QDateEdit(widget)
        date_edit.setCalendarPopup(True)
        date_edit.setDate(value)
        return date_edit

    def setEditorData(self, editor: QDateEdit, index: QModelIndex):
        date = index.data(Qt.UserRole)

        editor.setDate(date)
        editor.setCalendarPopup(True)
        logging.debug(f"setEditorData {index.row()}/{index.column()}")

    def setModelData(self, editor: QDateEdit, model, index: QModelIndex):
        date = editor.date().toPyDate()
        model.setData(index, date.strftime("%x"), Qt.DisplayRole)
        model.setData(index, date, Qt.UserRole)
        logging.debug(f"setModelData {index.row()}/{index.column()}")
        self.changed.emit(index, editor)

    def updateEditorGeometry(self, editor, option, index: QModelIndex):
        editor.setGeometry(option.rect)

    def paint(self, painter, option, index: QModelIndex):
        text = ""
        try:
            text = index.data(Qt.DisplayRole) # self.model.itemData(index)[Qt.DisplayRole]
        except Exception as e:
            logging.error(f"DateEditDelegate Exception {e}")

        if isinstance(text, datetime.date):
            text = text.strftime("%x")
        option.text = text
        QApplication.style().drawControl(QStyle.CE_ItemViewItem, option, painter)
