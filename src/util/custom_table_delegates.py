from typing import Callable
from PyQt5 import QtWidgets
from sqlalchemy import Null
from unidecode import unidecode
from lib.Genericos.log import logging

import copy
import datetime
import locale
import util.curr_formatter as curr
from PyQt5.QtCore import QEvent, QRect, QSize, QTimer, Qt, QModelIndex, pyqtSignal, QStringListModel
from PyQt5.QtGui import QBrush, QColor, QFont, QCursor
from PyQt5.QtWidgets import (
    QStyleOptionButton,
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

locale.setlocale(locale.LC_ALL, "pt_BR.utf8")


class EmitterItemDelegade(QStyledItemDelegate):
    changed = pyqtSignal(QModelIndex, QWidget)


class ComboBoxWithSearch(QComboBox):
    def __init__(self, parent: QWidget, items: list[str]):
        super().__init__(parent)
        self.items = items
        self.setEditable(True)
        model = QStringListModel(self.items)
        self.setModel(model)
        self.completer:QCompleter = QCompleter(self.model(), self)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompleter(self.completer)


# TODO: funciona perfeitamente, falta somente corrigir o mouseover
class ButtonDelegate(QStyledItemDelegate):
    def __init__(self, parent_table: QTableView, button: QPushButton, pressed_event: Callable[[QModelIndex], None]):
        super(ButtonDelegate, self).__init__(parent_table)
        self.parent_table = parent_table
        self.button:QPushButton = button
        self.pressed_index: QModelIndex = Null
        self.pressed_event = pressed_event
    
    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseButtonRelease:
            self.pressed_index = Null
            if self.timer:
                self.timer.stop()
                self.timer = Null
            self.pressed_event(index)

        if event.type() == QEvent.MouseButtonPress:
            self.timer = ButtonTimer(self)
            self.timer.start()

            self.pressed_index = index

        if event.type() == QEvent.Leave:
            logging.debug("Leave")
            self.pressed_index = Null

        if event.type() == QEvent.HoverEnter:
            logging.debug("HoverEnter")
            self.pressed_index = index

        if event.type() == QEvent.HoverLeave:
            logging.debug("HoverLeave")
            self.pressed_index = index

        return True

    def sizeHint(self, option, index) -> QSize:
        size = super(ButtonDelegate, self).sizeHint(option, index)
        size.setHeight(50)
        return size

    def paint(self, painter, option: QStyleOptionViewItem, index: QModelIndex):

        try:
            text = index.data(Qt.UserRole)
            if text:
                self.button.setText(str(text))
            # font = (index.data(Qt.FontRole) or QFont())
        except Exception as e:
            logging.error(f"IDLabelDelegate Exception {e}")

        painter.save()

        spacing = 6
        self.rect_button = QRect(
            option.rect.left() + int(spacing / 2),
            option.rect.top() + int(spacing / 2),
            option.rect.width() - spacing,
            option.rect.height() - spacing
        )

        option = QStyleOptionButton()
        option.initFrom(self.button)
        option.rect = copy.deepcopy( self.rect_button )

        if self.pressed_index == index:
            option.state = QtWidgets.QStyle.State_Sunken

        self.button.style().drawControl(QtWidgets.QStyle.CE_PushButton, 
            option, painter, self.button)
        btn_icon = self.button.icon().pixmap(24, 24)
        
        target_rect:QRect = copy.deepcopy( option.rect )
        target_rect.setX(option.rect.x() + int(option.rect.width() / 2) - int(btn_icon.rect().width() / 2))
        target_rect.setY(option.rect.y() + int(option.rect.height() / 2) - int(btn_icon.rect().height() / 2))

        if self.pressed_index == index:
            target_rect.setY(option.rect.y() + 3)

        target_rect.setWidth(btn_icon.width())
        target_rect.setHeight(btn_icon.height())

        if text:
            target_rect.setX(target_rect.x() - 16)
            target_rect.setWidth(btn_icon.width())

            text_rect = copy.deepcopy( self.rect_button )

            text_rect.setX(option.rect.x() + int(option.rect.width() / 2) - 20)
            if self.pressed_index == index:
                text_rect.setY(self.rect_button.y() + 5)
            else:
                text_rect.setY(self.rect_button.y() + 8)
            
            # FOR TESTING
            # background_brush = QBrush( QColor(255,0,0), Qt.SolidPattern)
            # painter.fillRect(text_rect, background_brush)

            painter.drawText(text_rect, Qt.AlignCenter + Qt.AlignVCenter, str(text))

        # FOR TESTING
        # background_brush = QBrush( QColor(255,0,0), Qt.SolidPattern)
        # painter.fillRect(target_rect, background_brush)

        painter.drawPixmap(target_rect, btn_icon, QRect(0, 0, 0, 0))
        painter.restore()

def rect_intersect_cursor(rect: QRect, table: QTableView): 

    pos = table.viewport().mapFromGlobal(QCursor.pos())

    tl = rect.topLeft()
    br = rect.bottomRight()

    x0 = tl.x()
    y0 = tl.y()
    x1 = br.x()
    y1 = br.y()

    intersect = \
        pos.x() > x0 and pos.x() < x1 and \
        pos.y() > y0 and pos.y() < y1
    
    return intersect
    

class ButtonTimer:
    def __init__(self, parent: ButtonDelegate) -> None:
        self.parent_delegate = parent
        self.brect = self.parent_delegate.rect_button
        self.timer = QTimer(parent)
        self.timer.timeout.connect(self.check_status)
        self.run_counter = 0

    def start(self):
        self.run_counter = 0
        self.timer.start(200)

    def stop(self):
        self.timer.stop()

    def check_status(self):
        self.run_counter += 1

        intersect = \
            rect_intersect_cursor(self.brect, self.parent_delegate.parent_table)
        # print(f"counter: {self.run_counter}, ", end="")
        # print(f"btn(x:{x0}, {pos.x()}, {x1}; y:{y0}, {pos.y()}, {y1}) is is?: {intersect}")
        
        if self.run_counter > 20 or not intersect:
            self.parent_delegate.pressed_index = Null
            self.timer.stop()

        self.parent_delegate.parent_table.viewport().repaint()


class IDLabelDelegate(QStyledItemDelegate):
    def __init__(self, parent_table: QTableView):
        super(IDLabelDelegate, self).__init__(parent_table)
        self.parent_table = parent_table

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
        model.setData(index, text, Qt.UserRole)
        model.setData(index, text, Qt.DisplayRole)
        logging.debug(f"setModelData {index.row()}/{index.column()}")
        self.changed.emit(index, editor)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class CurrencyEditDelegate(EmitterItemDelegade):
    def __init__(self, parent_table: QTableView):
        super(CurrencyEditDelegate, self).__init__(parent_table)
        self.parent_table = parent_table

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
        logging.debug("ComboBoxDelegate->commitAndCloseEditor")
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor, QStyledItemDelegate.NoHint)

    def setEditorData(self, editor: QComboBox, index):
        """Envia dados para o widget quando aberto"""
        logging.debug("ComboBoxDelegate->setEditorData")
        logging.debug("-- BLOCK SIGNALS -- ")
        self.blockSignals(True)
        editor.blockSignals(True)

        editor.lineEdit().setText(index.data(Qt.DisplayRole))
        editor.lineEdit().selectAll()
        editor.showPopup()

        logging.debug("-- UNBLOCK SIGNALS -- ")
        editor.blockSignals(False)
        self.blockSignals(False)

    def setModelData(self, editor: ComboBoxWithSearch, model, index: QModelIndex):
        """Na finalização envia os dados de volta para o modelo"""
        logging.debug("ComboBoxDelegate->setModelData")
        tipo_id_combo_index = editor.findText(editor.lineEdit().text())
        if tipo_id_combo_index is None or tipo_id_combo_index == -1 or tipo_id_combo_index >= len( editor.items ):
            logging.debug(f"tipo_id vazio! index: { tipo_id_combo_index }")
            return
        tipo_id = list(self.key_values.keys())[tipo_id_combo_index]
            
        model.setItemData(index,
            {
                Qt.DisplayRole: self.key_values.get(tipo_id),
                Qt.UserRole: tipo_id or -1,
                Qt.AccessibleTextRole: unidecode(self.key_values.get(tipo_id))
            },
        )
        # model.setData(index, tipo_id, Qt.UserRole)
        # model.setData(index, self.key_values.get(tipo_id), Qt.DisplayRole)
        self.changed.emit(index, editor)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class DateEditDelegate(EmitterItemDelegade):
    def __init__(self, parent_table: QTableView):
        super(DateEditDelegate, self).__init__(parent_table)
        self.parent_table = parent_table
        self.model = parent_table.model()

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
