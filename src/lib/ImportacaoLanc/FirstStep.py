#!

from enum import IntEnum, StrEnum, auto
import io
import locale
from typing import cast
import openpyxl

from PyQt5.QtGui import QCursor, QIcon
from lib.Genericos.QMessageHelper import MyMessagePopup
from lib.Genericos.log import logging
from lib import CustomToolbar
from util.curr_formatter import str_curr_to_int
from util import JanelaImportLancamentosSettings
import view.icons.icons as icons

from dataclasses import dataclass, field
from datetime import date, datetime
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from model import Categorias

from lib.ImportacaoLanc.TableLine import ImportarLancamentosTableLine


ToolButtonStyle = Qt.ToolButtonStyle
ItemFlag = Qt.ItemFlag
CursorShape = Qt.CursorShape


class TEXTS(StrEnum):
    ARQUIVO_N_EXCEL = 'Arquivo "{0}" não parece estar no formato excel.'
    SELECIONE_UMA_LINHA = "Favor selecionar ao menos uma linha."
    CATEGORIA_N_ENCONTRADA = 'Categoria com o nome "{0}" não encontrada.'
    CATEGORIA_VAZIA = "Categoria vazia."
    ERRO_AO_ADICIONAR_LINHA = "Erro ao adicionar linha {0}. Devem ao menos existir atributos: data, valor e descricao"
    LBL_SEPARADOR_MILHAR = "Separador Milhar:"
    LBL_SEPARADOR_DECIMAL = "Separador Decimal:"
    LBL_FORMATO_DATA = "Formato Data:"


class AbrirExcelErro(Exception):
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.message = TEXTS.ARQUIVO_N_EXCEL.format(self.filepath)
        super().__init__(self.message)


class NewLancamentoStatus(IntEnum):
    Nenhum = 0
    Erro = auto()  # impede registro de ser adicionado
    Aviso = auto()  # não impede registro de ser adicionado
    Info = auto()  # não impede registro de ser adicionado
    Sucesso = auto()  # depois de inserido apresenta este


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
    suggested_categ: int = field(default=-1)

    row_index: int = field(default=0)
    message_status: NewLancamentoStatus = field(default=NewLancamentoStatus.Nenhum)
    message: str = field(default="")
    id: int = field(default=0)
    new_categoria: str = field(default="")
    pode_inserir: bool = field(default=True)

    def valid(self) -> bool:
        return self.descricao != "" and self.data is not None  # and self.valor != 0

    @property
    def icon(self) -> QIcon:
        if self.message_status == NewLancamentoStatus.Sucesso:
            return icons.status_ok()
        elif self.message_status == NewLancamentoStatus.Nenhum:
            return icons.status_not_exec()
        elif self.message_status == NewLancamentoStatus.Erro:
            return icons.status_error()
        elif self.message_status == NewLancamentoStatus.Info:
            return icons.status_info()
        elif self.message_status == NewLancamentoStatus.Aviso:
            return icons.status_warning()
        else:
            return None


class FirstStepFrame(QWidget):
    # next button clicked send list of lancamentos
    passo_proximo = pyqtSignal(list)

    def __init__(self, parent: QWidget, settings: JanelaImportLancamentosSettings) -> None:
        super(FirstStepFrame, self).__init__(parent)

        # local vars
        self.settings = settings
        self.table = TableWidgetFirst(self)
        self.toolbar = self.get_toolbar()

        # layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.table)

        self.setLayout(layout)

        # model
        self.model_categoria = Categorias()

    def get_toolbar(self) -> CustomToolbar:
        toolbar = CustomToolbar()
        toolbar.setToolButtonStyle(ToolButtonStyle.ToolButtonTextBesideIcon)

        btn_next = toolbar.addAction(icons.results_next(), "Próximo passo")
        assert btn_next is not None
        btn_next.triggered.connect(self.on_proximo_passo)

        btn_remove_line = toolbar.addAction(icons.delete(), "Remover linha(s)")
        assert btn_remove_line is not None
        btn_remove_line.triggered.connect(self.on_remove_lines)

        return toolbar

    def on_remove_lines(self) -> None:
        unique_rows = list(dict.fromkeys([x.row() for x in self.table.selectedIndexes() if x.row() > 0]))
        unique_rows.sort(reverse=True)
        for sel in unique_rows:
            self.table.removeRow(sel)

    def on_proximo_passo(self):
        """Envia linhas selecionadas para a proxima tabela de preview"""
        array_indexes = list(map(lambda x: x.row(), self.table.selectedIndexes()))
        unique_indexes = list(set(array_indexes))

        # Nenhuma linha selecionada ou somente a primeira linha (dos combos)
        if len(unique_indexes) == 0 or (len(unique_indexes) == 1 and 0 in unique_indexes):
            MyMessagePopup(self).error(TEXTS.SELECIONE_UMA_LINHA)
            return

        mapping_cols = {}
        for col_index in range(self.table.columnCount()):
            column_combo = cast(QComboBox, self.table.cellWidget(0, col_index))
            if column_combo.currentData() != "":
                mapping_cols[column_combo.currentData()] = col_index

        selected_row_indexes = list(dict.fromkeys([x.row() for x in self.table.selectedIndexes() if x.row() > 0]))

        # carrega categorias todas as vezes pois alguma pode ter sido
        # adicionada por outro processo
        self.model_categoria.load()

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
            )
            for col in mapping_cols:
                cell = self.table.item(row_index, mapping_cols[col])
                if not cell:
                    continue
                cell_value = cell.text().strip()
                if col == "data":
                    data_value = self.parse_date(cell_value)
                    new_lancamento.__setattr__(col, data_value)
                elif col == "valor":
                    curr_value = self.parse_curr(cell_value)
                    new_lancamento.__setattr__(col, curr_value)
                elif col == "categoria_id":
                    categ_value = next(
                        (item.id for item in self.model_categoria.items if item.nm_categoria == cell_value), None
                    )
                    if not categ_value:
                        if cell_value != "":
                            new_lancamento.message = TEXTS.CATEGORIA_N_ENCONTRADA.format(cell_value)
                            new_lancamento.message_status = NewLancamentoStatus.Aviso
                            new_lancamento.new_categoria = cell_value
                        else:
                            new_lancamento.message = TEXTS.CATEGORIA_VAZIA
                            new_lancamento.message_status = NewLancamentoStatus.Aviso

                    new_lancamento.categoria_id = categ_value
                else:
                    new_lancamento.__setattr__(col, cell_value)
            if not new_lancamento.valid():
                text = TEXTS.ERRO_AO_ADICIONAR_LINHA.format(row_index + 1)
                new_lancamento.message = text
                new_lancamento.pode_inserir = False
                new_lancamento.message_status = NewLancamentoStatus.Erro
                logging.debug(text)

            new_lancamentos.append(new_lancamento)

        ###
        self.passo_proximo.emit(new_lancamentos)

        # salva mapeamento das colunas
        self.settings.import_col_position = mapping_cols

    def csv_to_table(self, file_name_fullpath: str):
        """
        Apos arquivo selecionado inicia o processamento e exibição das linhas na tabela
        """
        path = file_name_fullpath
        if not path:
            return
        # Limpa toda a tabela
        self.table.clear()
        try:
            in_mem_file = None
            # Abrir somente para leitura para não bloquear o arquivo
            with open(path, "rb") as file:
                in_mem_file = io.BytesIO(file.read())

            wb = openpyxl.load_workbook(in_mem_file)
        except Exception:
            raise AbrirExcelErro(file_name_fullpath)
        ws = wb.active

        QApplication.setOverrideCursor(QCursor(CursorShape.WaitCursor))

        column_count = len(list(ws.columns))
        self.table.setColumnCount(column_count)

        line = ImportarLancamentosTableLine(self)

        # Adiciona primeira linha da tabela para seleção de campo a ser mapeado
        self.table.insertRow(0)
        positions = self.settings.import_col_position

        for i in range(column_count):
            combo = line.get_combo()
            self.table.setCellWidget(0, i, combo)

        for position in positions:
            col_index = positions[position]
            combo = cast(QComboBox, self.table.cellWidget(0, col_index))
            index = combo.findData(position)
            if index:
                combo.setCurrentIndex(index)

        row_no = 1
        skipcount = 0

        # TODO: mudar para QProgressDialog
        prog_bar = QProgressBar()
        prog_bar.setRange(1, len(list(ws.rows)))
        layout = self.layout()
        assert layout is not None
        layout.addWidget(prog_bar)

        rowcount = 1  # starts at one because of the header line
        for row in ws.rows:
            rowcount += 1
        self.table.setRowCount(rowcount)

        for row in ws.iter_rows():
            rowvalues = [x.value for x in row if x.value != ""]
            if not rowvalues:
                skipcount += 1
                continue

            column_no = 0
            prog_bar.setValue(row_no)
            QApplication.processEvents()

            for cell in row:
                if hasattr(cell, "is_date") and cell.is_date and cell.value is not None:
                    cell_widget = QTableWidgetItem(cell.value.isoformat()[:10])
                elif isinstance(cell.value, float) or isinstance(cell.value, int):
                    cell_widget = QTableWidgetItem(str(cell.value))
                else:
                    cell_widget = QTableWidgetItem(cell.value)

                cell_widget.setFlags(ItemFlag.ItemIsSelectable | ItemFlag.ItemIsEnabled)
                self.table.setItem(row_no, column_no, cell_widget)
                column_no += 1

            row_no += 1

        logging.info(f"Adicionado {row_no} linhas. Descartadas: {skipcount}")

        wb.close()

        self.table.resizeColumnsToContents()

        layout.removeWidget(prog_bar)

        QApplication.restoreOverrideCursor()

    def parse_curr(self, curr_str: str):
        dec_separador = self.settings.separador_decimal
        mil_separador = self.settings.separador_milhar
        try:
            decimal_point = locale.localeconv()["decimal_point"]
            thousands_sep = locale.localeconv()["thousands_sep"]
            curr_str = curr_str.replace(mil_separador, str(thousands_sep)).replace(dec_separador, decimal_point)
            curr_int = str_curr_to_int(curr_str)
        except Exception as e:
            logging.debug(f"Erro importando valor em currency!, {e}")
            curr_int = 0

        return curr_int

    def parse_date(self, date_str: str) -> datetime.date:
        date_format = self.settings.formato_data
        try:
            date = datetime.strptime(date_str, date_format)
        except Exception as e:
            logging.debug("Erro importando valor em formato data!", e)
            date = None

        return date


class TableWidgetFirst(QTableWidget):
    """Primeira tabela do processo de importacao"""

    def __init__(self, parent: QWidget):
        super(TableWidgetFirst, self).__init__(parent)

        self.setColumnCount(0)


class ConfigImportacaoBlock(QWidget):
    def __init__(self, parent: QWidget, settings: JanelaImportLancamentosSettings) -> None:
        super().__init__(parent)

        # local vars
        self.settings = settings
        self.decimal_separator: QLineEdit | None = None
        self.mil_separator: QLineEdit | None = None
        self.date_format: QLineEdit | None = None

        # startup
        self.config_inputs()

        self.config_layout()

    def config_inputs(self):
        self.decimal_separator = QLineEdit(self.settings.separador_decimal)
        self.decimal_separator.setObjectName("separador_decimal")
        self.decimal_separator.editingFinished.connect(lambda: self._on_change_params(self.decimal_separator))
        self.mil_separator = QLineEdit(self.settings.separador_milhar)
        self.mil_separator.setObjectName("separador_milhar")
        self.mil_separator.editingFinished.connect(lambda: self._on_change_params(self.mil_separator))
        self.date_format = QLineEdit(self.settings.formato_data)
        self.date_format.setObjectName("formato_data")
        self.date_format.editingFinished.connect(lambda: self._on_change_params(self.date_format))

    def config_layout(self) -> None:
        layout = QHBoxLayout()
        layout.addWidget(QLabel(TEXTS.LBL_SEPARADOR_MILHAR))
        layout.addWidget(self.mil_separator)
        layout.addWidget(QLabel(TEXTS.LBL_SEPARADOR_DECIMAL))
        layout.addWidget(self.decimal_separator)
        layout.addWidget(QLabel(TEXTS.LBL_FORMATO_DATA))
        layout.addWidget(self.date_format)

        self.setLayout(layout)

    def _on_change_params(self, source: QLineEdit):
        """Grava configuracoes de importação diretamente nos settings"""
        logging.debug("Entrou no on change")
        if source.objectName() == "separador_decimal":
            self.settings.separador_decimal = source.text()
        elif source.objectName() == "separador_milhar":
            self.settings.separador_milhar = source.text()
        elif source.objectName() == "formato_data":
            self.settings.formato_data = source.text()
