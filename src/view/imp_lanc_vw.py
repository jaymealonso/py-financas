import locale
import logging
import os.path

import openpyxl
from PyQt5 import QtGui

import view.icons.icons as icons
from datetime import date, datetime
from dataclasses import dataclass
from model.Conta import Conta
from PyQt5.QtGui import QCursor, QCloseEvent
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
    QDialog, QProgressBar,
)
from model.Lancamento import Lancamentos as ORMLancamentos
from model.Categoria import Categorias as ORMCategorias
from view.TableLine import TableLine
from util.toaster import QToaster
from util.settings import Settings, JanelaImportLancamentosSettings
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
#        self.settings = self.global_settings.load_lanc_settings(self.conta_dc.id)
        self.settings: JanelaImportLancamentosSettings =\
            self.global_settings.load_impo_lanc_settings(self.conta_dc.id)

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
        self.model_categoria = ORMCategorias()
        self.model_categoria.load()

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle(
            f"Importar Lançamentos - (Conta {conta_dc.id} | {conta_dc.descricao})"
        )
        self.restore_geometry()
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        layout = QVBoxLayout()
        layout.addLayout(self.get_import_file_line())
        layout.addLayout(self.get_config_line())
        layout.addWidget(self.get_toolbar())
        layout.addWidget(self.get_table())

        self.setLayout(layout)

    def restore_geometry(self) -> None:
        self.setMinimumSize(800, 600)
        try:
            self.restoreGeometry(self.settings.dimensoes)
        except Exception as e:
            logging.error(str(e))
            self.resize(1600, 900)

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

        selected_row_indexes = list(
            dict.fromkeys(
                [x.row() for x in self.table.selectedIndexes() if x.row() > 0]
            )
        )
        created_lines = 0

        @dataclass
        class NewLancamento:
            """Classe local para organizar os valores e poder usar os __setattr__ mais a frente"""

            conta_id: int
            nr_referencia: str
            descricao: str
            descricao_user: str
            data: date
            valor: int
            categoria_id: int

            def valid(self) -> bool:
                return self.descricao and self.data and self.valor

        line = ImportarLancamentosTableLine(self)
        for row_index in selected_row_indexes:
            new_lancamento = NewLancamento(
                conta_id=int(self.conta_dc.id),
                nr_referencia="",
                descricao="Descrição lançamento",
                descricao_user="",
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
                elif col == "categoria_id":
                    categ_value = next(
                        (item.id for item in self.model_categoria.items if item.nm_categoria == cell_value), None)
                    new_lancamento.categoria_id = categ_value
                else:
                    new_lancamento.__setattr__(col, cell_value)
            if not new_lancamento.valid():
                logging.error(
                    f"Erro ao adicionar linha {row_index}. Devem ao menos existir atributos: data, valor e descricao")
                continue

            new_lancamento_id = self.model_lancamentos.add_new(
                conta_id=new_lancamento.conta_id,
                nr_referencia=new_lancamento.nr_referencia,
                descricao=new_lancamento.descricao,
                descricao_user=new_lancamento.descricao_user,
                data=new_lancamento.data,
                valor=new_lancamento.valor,
            )
            created_lines += 1
            if new_lancamento.categoria_id:
                self.model_lancamentos.update(new_lancamento_id, 'categoria_id', new_lancamento.categoria_id)

        # salva mapeamento das colunas
        self.settings.import_col_position = mapping_cols

        QToaster.showMessage(
            self,
            f"Foram criados {created_lines} novos lançamentos." if created_lines > 0
                else "Não foram criados lançamentos.",
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

        # TODO: mudar para QProgressDialog
        prog_bar = QProgressBar()
        prog_bar.setRange(1, len(list(ws.rows)))
        self.layout().addWidget(prog_bar)

        rowcount = 1 # starts at one because of the header line
        for row in ws.rows:
            rowcount += 1
        self.table.setRowCount(rowcount)

        for row in ws.iter_rows():
            rowvalues = [x.value for x in row if x.value != ""]
            if not rowvalues:
                skipcount += 1
                continue

            # self.table.insertRow(row_no)
            column_no = 0

            logging.info(f"Adding row {row_no} ...")
            prog_bar.setValue(row_no)
            QApplication.processEvents()

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

        self.layout().removeWidget(prog_bar)

        QApplication.restoreOverrideCursor()

    def get_table(self):
        self.table.setColumnCount(0)

        return self.table

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        """Fecha a janela mas salva a geometria dela quando apertar o ESC"""
        if event.key() == Qt.Key_Escape:
            self.settings.dimensoes = self.saveGeometry()
        super(ImportarLancamentosView, self).keyPressEvent(event)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.settings.dimensoes = self.saveGeometry()


class ImportarLancamentosTableLine(TableLine):
    LANCAMENTO_COLUMNS = {
        0: {"name": "(vazio)", "sql_colname": ""},
        1: {"name": "Número Ref.", "sql_colname": "nr_referencia"},
        2: {"name": "Descrição", "sql_colname": "descricao"},
        3: {"name": "Descrição Usuário", "sql_colname": "descricao_user"},
        4: {"name": "Data", "sql_colname": "data"},
        5: {"name": "Categorias", "sql_colname": "categoria_id"},
        6: {"name": "Valor", "sql_colname": "valor"},
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
