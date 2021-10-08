import locale
import datetime
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QItemDelegate, QComboBox, QApplication, QStyle, QTableView, QDateEdit, QStyledItemDelegate

locale.setlocale(locale.LC_ALL, "pt_br")


class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, values: dict, parent_table: QTableView):
        super(ComboBoxDelegate, self).__init__(parent_table)

        self.parent_table = parent_table
        self.key_values = values

    def createEditor(self, widget, option, index):
        print(f">>> Create editor, row: {index.row()}, col: {index.column()}")
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
        print(">>setEditorData")

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentData(), Qt.EditRole)
        print(">>setModelData")

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def paint(self, painter, option, index):
        text = ""
        try:
            model = self.parent_table.model()
            tipo_id = model.itemData(index)[0]
            text = self.key_values[tipo_id]
        except Exception as e:
            print(f"Exception {e}")
        option.text = text
        QApplication.style().drawControl(QStyle.CE_ItemViewItem, option, painter)


class DateEditDelegate(QStyledItemDelegate):
    def __init__(self, parent_table: QTableView):
        super(DateEditDelegate, self).__init__(parent_table)
        # self.date = ""
        self.parent_table = parent_table
        print("create date edit")

    def createEditor(self, widget, option, index):
        print(f">>> Create editor, row: {index.row()}, col: {index.column()}")
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
        print(">>setEditorData")

    def setModelData(self, editor: QDateEdit, model, index):
        model.setData(index, editor.date().toString("yyyy-MM-dd"), Qt.EditRole)
        print(">>setModelData")

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def paint(self, painter, option, index):
        text = ""
        try:
            date_striso = self.parent_table.model().item(index.row(), index.column()).text()
            date = datetime.datetime.fromisoformat(date_striso)
            text = date.strftime('%x')
        except Exception as e:
            print(f"Exception {e}")
        option.text = text
        QApplication.style().drawControl(QStyle.CE_ItemViewItem, option, painter)
