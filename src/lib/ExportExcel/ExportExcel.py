import datetime
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog
import moment
from openpyxl import Workbook
from util.my_dialog import MyDialog


class ExportExcel():
    def __init__(self, dialog: MyDialog, model:QtGui.QStandardItemModel, conta_descricao:str) -> None:
        self.parent = dialog
        self.model = model
        self.conta_descricao = conta_descricao

    def export(self, prefix:str = "") -> None:
        datetime_str: str = moment.now().isoformat().replace(":", "_")[:19]
        default_filename: str = f"{prefix}-{self.conta_descricao}-{datetime_str}.xlsx"
        dialog = QFileDialog()
        (filename, selectedFilter) = dialog.getSaveFileName(
            self.parent, "Exportar planilha", default_filename
        )
        if filename is None or filename == "":
            return

        wb = Workbook()
        ws = wb.active

        column_count = self.model.columnCount()
        row_count = self.model.rowCount()

        col_titles = map(
            lambda index: self.model.horizontalHeaderItem(index).text(),
            [i for i in range(column_count)],
        )
        ws.append(list(col_titles))

        for row_index in range(row_count):
            row_values = []
            for col_index in range(column_count):
                value = ""
                value = self.model.index(row_index, col_index).data(Qt.UserRole)
                if value:
                    if isinstance(value, int):
                        value = value / 100
                    elif isinstance(value, datetime.datetime):
                        value = value.strftime("%x")
                else:                        
                    value = self.model.index(row_index, col_index).data(Qt.DisplayRole)
                row_values.append(value)
            ws.append(row_values)

        wb.save(filename)
