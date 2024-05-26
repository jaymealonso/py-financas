#!

import locale
import stat

from PyQt5.QtGui import QCursor
import openpyxl
from lib.Genericos.log import logging
from util.curr_formatter import str_curr_to_int
from util.settings import JanelaImportLancamentosSettings
import view.icons.icons as icons

from dataclasses import dataclass, field
from datetime import date, datetime
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import ( QApplication, QComboBox, QMessageBox, QProgressBar, 
    QTableWidget, QTableWidgetItem, QToolBar, QVBoxLayout, QWidget )
from model.Categoria import Categorias as ORMCategorias

from lib.ImportacaoLanc.TableLine import ImportarLancamentosTableLine


class AbrirExcelErro(Exception):
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.message = f'Arquivo "{self.filepath}" não parece estar no formato excel.'
        super().__init__(self.message)

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
    
    row_index: int = field(default=0)
    status_import: str = field(default="")
    id: int = field(default=0)

    def valid(self) -> bool:
        return self.descricao and self.data and self.valor


class FirstStepFrame(QWidget):
    # next button clicked send list of lancamentos
    passo_proximo = pyqtSignal(list)

    def __init__(self, parent: QWidget, settings: JanelaImportLancamentosSettings) -> None:
        super(FirstStepFrame, self).__init__(parent)

        # local vars
        self.settings = settings
        self.table = TableWidgetFirst(self)
        self.toolbar = QToolBar()

        # layout
        layout = QVBoxLayout()
        layout.addWidget(self.get_toolbar())
        layout.addWidget(self.table)

        self.setLayout(layout)

        # model
        self.model_categoria = ORMCategorias()
        self.model_categoria.load()

    def get_toolbar(self) -> QToolBar:
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        btn_next = self.toolbar.addAction(icons.results_next(), "Próximo passo")
        btn_next.triggered.connect( self.on_proximo_passo )

        btn_remove_line = self.toolbar.addAction(icons.delete(), "Remover linha(s)")
        btn_remove_line.triggered.connect(self.on_remove_lines)

        return self.toolbar

    def on_remove_lines(self) -> None:
        unique_rows = list(
            dict.fromkeys(
                [x.row() for x in self.table.selectedIndexes() if x.row() > 0]
            )
        )
        unique_rows.sort(reverse=True)
        for sel in unique_rows:
            self.table.removeRow(sel)

    def on_proximo_passo(self):
        """ Envia linhas selecionadas para a proxima tabela de preview """
        if len( self.table.selectedIndexes() ) == 0:
            QMessageBox.critical(self, "Erro", "Favor selecionar ao menos uma linha.")
            return
        
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

        new_lancamentos = []
        for row_index in selected_row_indexes:
            new_lancamento = NewLancamento(
                conta_id=0,
                nr_referencia="",
                descricao="Descrição lançamento",
                descricao_user="",
                data=datetime.now(),
                valor=0,
                categoria_id=None,
                row_index=row_index + 1,
                status_import="",
            )
            for col in mapping_cols:
                cell = self.table.item(row_index, mapping_cols[col])
                if not cell:
                    continue
                cell_value = cell.text()
                if col == "data":
                    data_value = self.parse_date(cell_value)
                    new_lancamento.__setattr__(col, data_value)
                elif col == "valor":
                    curr_value = self.parse_curr(cell_value)
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

            new_lancamentos.append(new_lancamento)

        ###
        self.passo_proximo.emit(new_lancamentos)

        # salva mapeamento das colunas
        self.settings.import_col_position = mapping_cols

    def csv_to_table(self, file_name_fullpath:str):
        """
        Apos arquivo selecionado inicia o processamento e exibição das linhas na tabela
        """
        path = file_name_fullpath
        if not path:
            return
        # Limpa toda a tabela
        self.table.clear()
        try:
            wb = openpyxl.load_workbook(path)
        except Exception:
            raise AbrirExcelErro(file_name_fullpath)
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
                if hasattr(cell, "is_date") and cell.is_date and cell.value is not None:
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

    def parse_curr(self, curr_str: str):
        dec_separador = self.settings.separador_decimal
        mil_separador = self.settings.separador_milhar
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
        date_format = self.settings.formato_data
        try:
            date = datetime.strptime(date_str, date_format)
        except Exception as e:
            logging.error("Erro importando valor em formato data!", e)
            date = None

        return date        


class TableWidgetFirst(QTableWidget):
    """ Primeira tabela do processo de importacao """

    def __init__(self, parent: QWidget):
        super(TableWidgetFirst, self).__init__(parent)
        
        self.setColumnCount(0)

