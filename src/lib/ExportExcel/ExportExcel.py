import datetime
from decimal import Decimal
from typing import List
import moment
from openpyxl import Workbook

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog
from util import MyDialog

ItemDataRole = Qt.ItemDataRole


class ExportExcel:
    def __init__(self, dialog: MyDialog, model: QtGui.QStandardItemModel, conta_descricao: str) -> None:
        self.parent = dialog
        assert model is not None
        self.model = model
        self.conta_descricao = conta_descricao

    def export(self, prefix: str = "", currency_cols_indexes: List[int] = []) -> None:
        datetime_str: str = moment.now().isoformat().replace(":", "_")[:19]
        default_filename: str = f"{prefix}-{self.conta_descricao}-{datetime_str}.xlsx"
        dialog = QFileDialog()
        (filename, selectedFilter) = dialog.getSaveFileName(self.parent, "Exportar planilha", default_filename)
        if filename is None or filename == "":
            return

        wb = Workbook()
        ws = wb.active

        column_count = self.model.columnCount()
        row_count = self.model.rowCount()

        def get_header_text(index):
            return self.model.horizontalHeaderItem(index).text()

        col_titles = map(
            lambda index: get_header_text(index),  # self.model.horizontalHeaderItem(index).text(),
            [i for i in range(column_count)],
        )
        ws.append(list(col_titles))

        for row_index in range(row_count):
            row_values = []
            for col_index in range(column_count):
                value = ""

                value_display = self.model.index(row_index, col_index).data(ItemDataRole.DisplayRole)
                value_raw = self.model.index(row_index, col_index).data(ItemDataRole.UserRole)
                is_currency_col = col_index in currency_cols_indexes
                if value_display and not is_currency_col:
                    value = value_display
                else:
                    if value_raw:
                        if isinstance(value_raw, int) and is_currency_col:
                            value = value_raw / 100
                        elif isinstance(value_raw, int):
                            value = value_raw
                        elif isinstance(value_raw, Decimal):
                            value = value_raw
                        elif isinstance(value_raw, datetime.datetime):
                            value = value_raw.strftime("%x")

                row_values.append(value)
            ws.append(row_values)

        wb.save(filename)
