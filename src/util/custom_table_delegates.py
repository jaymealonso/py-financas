import datetime
import locale
import logging
import util.curr_formatter as curr
from collections.abc import Callable
from PyQt5.QtCore import QEvent, QObject, Qt, QModelIndex, pyqtSignal, QStringListModel, QPoint, QTimer, QSortFilterProxyModel
from PyQt5.QtGui import QColor, QHideEvent, QIcon, QRegion, QFont, QPalette
from PyQt5.QtWidgets import (
        QStylePainter, QStyleOptionComboBox,
    QAbstractItemView,
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

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


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
        # self.clearEditText()
        self.completer = QCompleter(self.model(), self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        # self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.setCompleter(self.completer)

    # def eventFilter(self, obj: QObject | None, event: QEvent | None) -> bool:
    #     eventType = event.type()
    #     if eventType in (
    #         event.Type.KeyPress, event.Type.KeyRelease, 
    #         event.Type.MouseButtonPress, event.Type.MouseMove, 
    #         event.Type.MouseButtonRelease, 
    #         event.Type.Wheel, 
    #     ):
    #         logging.debug("event ignored")
    #         return True
    #     if eventType == event.Type.Hide:
    #         logging.debug("show event")
    #         obj.show()
    #         return True
    #     elif eventType == event.Type.FocusOut:
    #         logging.debug("focus out")
    #         QTimer.singleShot(0, obj.setFocus)
    #         return True
    #     return super().eventFilter(obj, event)

    def hidePopup(self) -> None:
        logging.debug("BLOCKED *** Hide pop")
        pass
        # return super().hidePopup()




# TODO: fazer um delegate para os botoes, este abaixo ainda nao funciona e ainda nao está sendo usado
class ButtonDelegate(QStyledItemDelegate):
    pressed = pyqtSignal(QModelIndex, QWidget)

    def __init__(self, parent_table: QTableView, function: Callable[[int], None]):
        super(ButtonDelegate, self).__init__(parent_table)
        self.function = function
        self.parent_table = parent_table
        logging.debug("Initialize Button")

    def createEditor(self, widget, option, index):
        button = self.get_del_button(widget)
        model = self.parent_table.model()
        lancamento_id = model.itemData(model.index(0, 0)).get(Qt.UserRole)
        button.clicked.connect(lambda: self.function(lancamento_id))
        return button

    def setEditorData(self, editor, index):
        pass

    def setModelData(self, editor, model, index):
        pass

    def get_del_button(self, widget):
        del_pbutt = QPushButton(widget)
        del_pbutt.setToolTip("Eliminar Lançamento")
        del_pbutt.setIcon(icons.delete())
        # del_pbutt.clicked.connect(lambda: parent.on_del_lancamento(lancamento_id))
        return del_pbutt

    # @staticmethod
    # def get_button(self, tooltip: str, icon: QIcon, function:callable()) -> QPushButton:
    #     del_pbutt = QPushButton()
    #     del_pbutt.setToolTip(tooltip)
    #     del_pbutt.setIcon(icon)
    #     del_pbutt.clicked.connect(lambda: function)
    #     return del_pbutt

    def paint(self, painter, option: QStyleOptionViewItem, index: QModelIndex):
        painter.save()
        painter.translate(option.rect.topLeft())
        self.button.setGeometry(option.rect)
        self.button.render(painter, QPoint(), QRegion(self.button.rect()), QWidget.DrawChildren)
        painter.restore()


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
            item_data = self.parent_table.model().itemData(index)
            text = item_data.get(Qt.UserRole)  # "item_data[Qt.DisplayRole]
            font = (item_data.get(Qt.FontRole) or QFont())
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
            # if isinstance(self.parent_table.model(), QSortFilterProxyModel):
            #     item_data = self.parent_table.model().sourceModel().itemData(index)
            # else:
            #     item_data = self.parent_table.model().itemData(index)
            # if not item_data:
            #     return
            value = index.data(Qt.UserRole) # item_data.get(Qt.UserRole)
            text  = index.data(Qt.DisplayRole) # item_data.get(Qt.DisplayRole)
            font  = index.data(Qt.FontRole) or QFont() # (item_data.get(Qt.FontRole) or QFont())
            # font = (item_data.get(Qt.FontRole) or QFont())
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
        model = self.parent_table.model()
        value = index.data(Qt.UserRole) # model.itemData(index)[Qt.UserRole]
        curr_edit = QCurrencyLineEdit(widget, value)
        return curr_edit

    def setEditorData(self, editor: QCurrencyLineEdit, index):
        model = self.parent_table.model()
        value: float = index.data(Qt.UserRole) / 100 # model.itemData(index)[Qt.UserRole] / 100
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
            value = index.data(Qt.UserRole) 
            text = index.data(Qt.DisplayRole)
        #     if isinstance(self.parent_table.model(), QSortFilterProxyModel):
        #         item_data = self.parent_table.model().sourceModel().itemData(index)
        #         if not item_data:
        #             item_data = self.parent_table.model().itemData(index)
        #     else:
        #         item_data = self.parent_table.model().itemData(index)                
        #     # item_data = self.parent_table.model().itemData(index)
        #     try:
        #         value = item_data[Qt.UserRole] # if Qt.UserRole in item_data else 0
        #     except Exception as e1:
        #         value = item_data[Qt.EditRole] # if Qt.EditRole in item_data else 0
        #     text = item_data[Qt.DisplayRole] # if Qt.DisplayRole in item_data else 0
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

    # def paint(self, painter, option, index):
    #     if isinstance(self.parent(), QAbstractItemView):
    #         self.parent().openPersistentEditor(index)
    #     super(ComboBoxDelegate, self).paint(painter, option, index)

    # def updateEditorGeometry(self, editor, option, index):
    #     editor.setGeometry(option.rect)

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
        logging.debug(f"Combobox Clear")
        editor.clearEditText()
        logging.debug(f"Show popup")
        editor.showPopup()

    def setModelData(self, editor: ComboBoxWithSearch, model, index):
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
            value = self.model.itemData(index)[Qt.UserRole]
        except Exception as e:
            logging.debug(f"sem data, erro: {e}")
            value = datetime.date.today()
        date_edit = QDateEdit(widget)
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
            logging.error(f"DateEditDelegate Exception {e}")

        if isinstance(text, datetime.date):
            text = text.strftime("%x")
        option.text = text
        QApplication.style().drawControl(QStyle.CE_ItemViewItem, option, painter)
