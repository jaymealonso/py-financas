import os.path
from datetime import datetime
import openpyxl
import view.icons.icons as icons
from model.Conta import Conta
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QTableWidgetItem,
    QToolBar,
    QApplication,
    QLabel,
    QComboBox,
    QMessageBox,
    QDialog
)
from model.Lancamento import Lancamentos
from view.TableLine import TableLine
from util.toaster import QToaster


class ImportarLancamentosView(QDialog):
    def __init__(self, parent: QWidget, conta_dc: Conta):
        self.btn_procurar = QPushButton("Procurar...")
        self.table = QTableWidget()
        self.toolbar = QToolBar()
        self.file_path = QLineEdit()
        self.decimal_separator = QLineEdit(",")
        self.mil_separator = QLineEdit(".")
        self.date_format = QLineEdit("%d-%m-%Y")
        self.conta_dc = conta_dc

        self.model_lancamentos = Lancamentos(conta_dc)

        super(ImportarLancamentosView, self).__init__(parent)

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle(
            f"Importar Lançamentos - (Conta {conta_dc.id} | {conta_dc.descricao})"
        )
        self.setMinimumSize(800, 600)
        self.resize(1600, 900)

        layout = QVBoxLayout()
        layout.addLayout(self.get_import_file_line())
        layout.addLayout(self.get_config_line())
        layout.addWidget(self.get_toolbar())
        layout.addWidget(self.get_table())

        self.setLayout(layout)

    def get_import_file_line(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Importar arquivo:"))
        layout.addWidget(self.file_path)
        self.file_path.setEnabled(False)
        layout.addWidget(self.btn_procurar)
        self.btn_procurar.clicked.connect(self.on_procurar_clicked)
        return layout

    def get_config_line(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Separador Milhar:"))
        layout.addWidget(self.mil_separator)
        layout.addWidget(QLabel("Separador Decimal:"))
        layout.addWidget(self.decimal_separator)
        layout.addWidget(QLabel("Formato Data:"))
        layout.addWidget(self.date_format)

        return layout

    def get_toolbar(self) -> QToolBar:
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        btn_remove_line = self.toolbar.addAction(icons.delete(), "Remover linha(s)")
        btn_remove_line.triggered.connect(self.on_remove_lines)

        btn_import_lanc = self.toolbar.addAction(icons.add(), "Importar linha(s)")
        btn_import_lanc.triggered.connect(self.on_import_linhas)

        return self.toolbar

    def on_remove_lines(self):
        unique_rows = list(
            dict.fromkeys(
                [x.row() for x in self.table.selectedIndexes() if x.row() > 0]
            )
        )
        unique_rows.sort(reverse=True)
        for sel in unique_rows:
            self.table.removeRow(sel)

    def on_import_linhas(self):
        mapping_cols = {}
        for col_index in range(self.table.columnCount()):
            column_combo: QComboBox = self.table.cellWidget(0, col_index)
            if column_combo.currentData() != "":
                mapping_cols[column_combo.currentData()] = col_index

        unique_rows = list(
            dict.fromkeys(
                [x.row() for x in self.table.selectedIndexes() if x.row() > 0]
            )
        )

        line = ImportarLancamentosTableLine(self)
        for row_index in unique_rows:
            new_lancamento = Lancamento(
                id=None,
                conta_id=int(self.conta_dc.id),
                nr_referencia="",
                descricao="Descrição lançamento",
                data=datetime.now(),
                valor=0,
                categoria_id=None,
            )
            for col in mapping_cols:
                cell = self.table.item(row_index, mapping_cols[col])
                if not cell:
                    continue
                cell_value = cell.text()
                if col == "data":
                    data_value = line.parse_date(cell_value)
                    new_lancamento.__setattr__(col, data_value)
                elif col == "valor":
                    curr_value = line.parse_curr(cell_value)
                    new_lancamento.__setattr__(col, curr_value)
                else:
                    new_lancamento.__setattr__(col, cell_value)

            self.model_lancamentos.add_new(new_lancamento)
        QToaster.showMessage(
            self,
            f"Foram criados {len(unique_rows)} novos lançamentos.",
            closable=False,
            timeout=2000,
            corner=Qt.BottomRightCorner,
        )

    def on_procurar_clicked(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        (fileName, selectedFilter) = dialog.getOpenFileName()
        if os.path.isfile(fileName):
            self.file_path.setText(fileName)
            self._on_importar_clicked()

    def _on_importar_clicked(self):
        path = self.file_path.text()
        if not path:
            return
        # Limpa toda a tabela
        self.table.clear()
        try:
            wb = openpyxl.load_workbook(path)
        except:
            QMessageBox(
                QMessageBox.Warning,
                "Erro no formato",
                f'Arquivo "{self.file_path.text()}" não parece estar no formato excel.',
                QMessageBox.Ok,
            ).exec_()
            self.file_path.setText("")
            return
        ws = wb.active

        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

        column_count = len(list(ws.columns))
        self.table.setColumnCount(column_count)

        line = ImportarLancamentosTableLine(self)

        self.table.insertRow(0)
        for i in range(column_count):
            self.table.setCellWidget(0, i, line.get_combo())

        row_no = 1
        skipcount = 0
        for row in ws.iter_rows():
            rowvalues = [x.value for x in row if x.value != None]
            if not rowvalues:
                skipcount += 1
                continue

            self.table.insertRow(row_no)
            column_no = 0
            print(f"Adding row {row_no} cols: ", end=" ")
            for cell in row:
                if hasattr(cell, "is_date") and cell.is_date:
                    cell_widget = QTableWidgetItem(cell.value.isoformat()[:10])
                elif isinstance(cell.value, float) or isinstance(cell.value, int):
                    cell_widget = QTableWidgetItem(str(cell.value))
                else:
                    cell_widget = QTableWidgetItem(cell.value)
                cell_widget.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(row_no, column_no, cell_widget)
                print(f"{column_no},", end=" ")
                column_no += 1
            print(" Finished ROW!")

            row_no += 1

        print(f"SkipCount: {skipcount}")

        self.table.resizeColumnsToContents()

        QApplication.restoreOverrideCursor()

    def get_table(self):
        self.table.setColumnCount(0)

        return self.table


class ImportarLancamentosTableLine(TableLine):
    LANCAMENTO_COLUMNS = {
        -1: {"name": "(vazio)", "sql_colname": ""},
        0: {"name": "Número Ref.", "sql_colname": "nr_referencia"},
        1: {"name": "Descrição", "sql_colname": "descricao"},
        2: {"name": "Data", "sql_colname": "data"},
        3: {"name": "Categorias", "sql_colname": "categoria_id"},
        4: {"name": "Valor", "sql_colname": "valor"},
    }

    def __init__(self, parent_view: ImportarLancamentosView):
        super(TableLine, self).__init__()
        self.parentView = parent_view

    def get_combo(self):
        combo = QComboBox()
        for col in self.LANCAMENTO_COLUMNS.values():
            combo.addItem(col["name"], col["sql_colname"])

        return combo

    def parse_curr(self, curr_str: str):
        decimal_separator = self.parentView.decimal_separator.text()
        mil_separator = self.parentView.mil_separator.text()
        try:
            curr_str = curr_str.replace(mil_separator, "").replace(
                decimal_separator, "."
            )
            curr_int = int(curr_str)
        except:
            print("Erro importando valor em currency!")
            curr_int = 0

        return curr_int

    def parse_date(self, date_str: str) -> datetime.date:
        date_format = self.parentView.date_format.text()
        try:
            date = datetime.strptime(date_str, date_format)
        except Exception as e:
            print("Erro importando valor em formato data!", e)
            date = None

        return date
