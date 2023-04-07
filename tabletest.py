from PyQt5.QtCore import (
    Qt,
    QModelIndex,
    QAbstractTableModel,
    QStringListModel,
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QComboBox,
    QTableView,
    QStyledItemDelegate,
    QVBoxLayout,
    QCompleter,
)


class ComboBoxWithSearch(QComboBox):
    def __init__(self, parent, items):
        super().__init__(parent)
        self.items = items
        self.setEditable(True)

        model = QStringListModel(self.items)
        self.setModel(model)
        self.completer = QCompleter(self.model(), self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompleter(self.completer)

    # def on_text_changed(self, text):
    #     matching_items = [item for item in self.items if text.lower() in item.lower()]
    #     print(f"{text} >> {len(matching_items)}")
    #     self.model().setStringList(matching_items)

    #     if matching_items:
    #         print("matched!")
    #         self.completer.complete()
    #         self.setCurrentIndex(self.findText(matching_items[0]))


class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, items=[]):
        super().__init__(parent)
        self.parent = parent
        self.items = items

    def createEditor(self, parent, option, index):
        editor = ComboBoxWithSearch(parent, self.items)
        editor.currentIndexChanged.connect(self.commitAndCloseEditor)
        print("createEditor")
        return editor

    def setEditorData(self, editor, index):
        print("setEditorData")
        # text = index.model().data(index, Qt.EditRole)
        # editor.setCurrentText(text)
        editor.setCurrentText("")
        # editor.lineEdit().setText("")

    def setModelData(self, editor, model, index):
        text = editor.currentText()
        model.setData(index, text, Qt.EditRole)

    def commitAndCloseEditor(self):
        print("commitAndCloseEditor")
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor, QStyledItemDelegate.NoHint)


# class TableModel(QAbstractTableModel):
class TableModel(QStandardItemModel):
    def __init__(self, data):
        super().__init__(len(data), len(data[0]))
        self._data = data

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._data[0])

    def data(self, index, role):
        if not index.isValid():
            return None

        row, col = index.row(), index.column()
        value = self._data[row][col]

        if role == Qt.DisplayRole or role == Qt.EditRole:
            return value

        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            row, col = index.row(), index.column()
            self._data[row][col] = value
            self.dataChanged.emit(index, index)
            return True
        return False


if __name__ == "__main__":
    app = QApplication([])
    items = [
        "Apple",
        "Banana",
        "Bola",
        "Butter",
        "Cherry",
        "Durian",
        "Elderberry",
        "Fig",
    ]

    table_data = [
        ["Apple", "1"],
        ["Banana", "2"],
        ["Cherry", "3"],
        ["Durian", "4"],
        ["Elderberry", "5"],
        ["Fig", "6"],
    ]

    model = TableModel(table_data)
    view = QTableView()

    view.setModel(model)
    view.editTriggers = QAbstractItemView.CurrentChanged  # <-- Added line

    delegate = ComboBoxDelegate(view, items=items)
    view.setItemDelegateForColumn(0, delegate)

    view.resize(800, 600)
    view.show()
    app.exec_()
