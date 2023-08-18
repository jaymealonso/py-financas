import locale
import logging
import os.path
import openpyxl
import view.icons.icons as icons
from datetime import date, datetime
from dataclasses import dataclass
from model.Conta import Conta
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt, pyqtSignal
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
    QDialog,
)
from model.Lancamento import Lancamentos as ORMLancamentos
from view.TableLine import TableLine
from util.toaster import QToaster
from util.settings import Settings
from util.curr_formatter import str_curr_to_int

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


class ImportarLancamentosView(QDialog):
    def __init__(self, parent: QWidget, conta_dc: Conta):
        super(ImportarLancamentosView, self).__init__(parent)

        self.conta_dc = conta_dc
        self.global_settings = Settings()
        self.settings = self.global_settings.load_lanc_settings(self.conta_dc.id)

        self.btn_procurar = QPushButton("Procurar...")
        self.table = QTableWidget()
        self.toolbar = QToolBar()
        self.file_path = QLineEdit()
        self.decimal_separator = QLineEdit(self.settings.separador_decimal)
        self.decimal_separator.setObjectName("separador_decimal")
        self.decimal_separator.editingFinished.connect(
            lambda: self._on_change_params(self.decimal_separator)
        )
        self.mil_separator = QLineEdit(self.settings.separador_milhar)
        self.mil_separator.setObjectName("separador_milhar")
        self.mil_separator.editingFinished.connect(
            lambda: self._on_change_params(self.mil_separator)
        )
        self.date_format = QLineEdit(self.settings.formato_data)
        self.date_format.setObjectName("formato_data")
        self.date_format.editingFinished.connect(
            lambda: self._on_change_params(self.date_format)
        )

        self.model_lancamentos = ORMLancamentos(conta_dc)

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

    def _on_change_params(self, source: QLineEdit):
        logging.debug("Entrou no on change")
        if source.objectName() == "separador_decimal":
            self.settings.separador_decimal = source.text()
        elif source.objectName() == "separador_milhar":
            self.settings.separador_milhar = source.text()
        elif source.objectName() == "formato_data":
            self.settings.formato_data = source.text()

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
        """
        Gera lançamentos a partir das linhas selecionadas
        """
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

        @dataclass
        class NewLancamento:
            """Classe local para organizar os valores e poder usar os __setattr__ mais a frente"""

            conta_id: int
            nr_referencia: str
            descricao: str
            data: date
            valor: int
            categoria_id: int

        line = ImportarLancamentosTableLine(self)
        for row_index in unique_rows:
            new_lancamento = NewLancamento(
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

            self.model_lancamentos.add_new(
                conta_id=new_lancamento.conta_id,
                nr_referencia=new_lancamento.nr_referencia,
                descricao=new_lancamento.descricao,
                data=new_lancamento.data,
                valor=new_lancamento.valor,
            )

        # salva mapeamento das colunas
        self.settings.import_col_position = mapping_cols

        QToaster.showMessage(
            self,
            f"Foram criados {len(unique_rows)} novos lançamentos.",
            closable=False,
            timeout=2000,
            corner=Qt.BottomRightCorner,
        )

    def on_procurar_clicked(self):
        """
        Chama popup de procura arquivo a ser importado
        """
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        (fileName, selectedFilter) = dialog.getOpenFileName()
        if os.path.isfile(fileName):
            self.file_path.setText(fileName)
            self._on_importar_clicked()

    def _on_importar_clicked(self):
        """
        Apos arquivo selecionado inicia o processamento e exibição das linhas na tabela
        """
        path = self.file_path.text()
        if not path:
            return
        # Limpa toda a tabela
        self.table.clear()
        try:
            wb = openpyxl.load_workbook(path)
        except Exception as e:
            QMessageBox(
                QMessageBox.Warning,
                f"Erro no formato {e}",
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

        # Adiciona primeira linha da tabela para seleção de campo a ser mapeado
        self.table.insertRow(0)
        positions: dict[int, set] = self.settings.import_col_position
        for i in range(column_count):
            combo = line.get_combo()
            filled_col_name = next((x for x, y in positions.items() if y == i), None)
            if filled_col_name is not None:
                for index in range(combo.count()):
                    if combo.itemData(index) == filled_col_name:
                        combo.setCurrentIndex(index)
                        break
            self.table.setCellWidget(0, i, combo)

        row_no = 1
        skipcount = 0
        for row in ws.iter_rows():
            rowvalues = [x.value for x in row if x.value != ""]
            if not rowvalues:
                skipcount += 1
                continue

            self.table.insertRow(row_no)
            column_no = 0
            logging.info(f"Adding row {row_no} ...")
            for cell in row:
                if hasattr(cell, "is_date") and cell.is_date and not cell.value is None:
                    cell_widget = QTableWidgetItem(cell.value.isoformat()[:10])
                elif isinstance(cell.value, float) or isinstance(cell.value, int):
                    cell_widget = QTableWidgetItem(str(cell.value))
                else:
                    cell_widget = QTableWidgetItem(cell.value)
                cell_widget.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(row_no, column_no, cell_widget)
                column_no += 1

            row_no += 1

        logging.info(f"SkipCount: {skipcount}")

        self.table.resizeColumnsToContents()

        QApplication.restoreOverrideCursor()

    def get_table(self):
        self.table.setColumnCount(0)

        return self.table


class ImportarLancamentosTableLine(TableLine):
    LANCAMENTO_COLUMNS = {
        0: {"name": "(vazio)", "sql_colname": ""},
        1: {"name": "Número Ref.", "sql_colname": "nr_referencia"},
        2: {"name": "Descrição", "sql_colname": "descricao"},
        3: {"name": "Data", "sql_colname": "data"},
        4: {"name": "Categorias", "sql_colname": "categoria_id"},
        5: {"name": "Valor", "sql_colname": "valor"},
    }

    def __init__(self, parent_view: ImportarLancamentosView):
        super(TableLine, self).__init__()
        self.parentView = parent_view

    def get_combo(self) -> QComboBox:
        combo = QComboBox()
        for index, value in self.LANCAMENTO_COLUMNS.items():
            name = value["name"]
            sql_colname = value["sql_colname"]
            combo.addItem(name, sql_colname)

        return combo

    def parse_curr(self, curr_str: str):
        dec_separador = self.parentView.decimal_separator.text()
        mil_separador = self.parentView.mil_separator.text()
        try:
            decimal_point = locale.localeconv()["decimal_point"]
            thousands_sep = locale.localeconv()["thousands_sep"]
            curr_str = curr_str.replace(mil_separador, thousands_sep).replace(
                dec_separador, decimal_point
            )
            curr_int = str_curr_to_int(curr_str)
        except Exception as e:
            logging.error(f"Erro importando valor em currency!, {e}")
            curr_int = 0

        return curr_int

    def parse_date(self, date_str: str) -> datetime.date:
        date_format = self.parentView.date_format.text()
        try:
            date = datetime.strptime(date_str, date_format)
        except Exception as e:
            logging.error("Erro importando valor em formato data!", e)
            date = None

        return date
