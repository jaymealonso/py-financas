import moment
from openpyxl import Workbook
import PyQt5.QtGui as QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QToolBar,
    QTableWidgetItem,
    QDialog,
    QFileDialog,
    QSizePolicy,
    QLineEdit,
    QSplitter,
)
from util.settings import JanelaVisaoMensalSettings, Settings
import logging
import view.contas_vw as cv
import view.icons.icons as icons
from view.TableLine import TableLine
from model.Conta import Conta
from model.VisaoMensal import VisaoMensal
from util.curr_formatter import str_curr_to_int
from view.lanc_vw import LancamentosView

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


class VisaoGeralView(QDialog):
    def __init__(self, parent: QWidget, conta_dc: Conta):
        self.toolbar: QToolBar = None
        self.table: QTableWidget = None
        self.line = VisaoGeralViewLine()
        self.conta_dc = conta_dc
        self.model_visao_mensal = VisaoMensal(self.conta_dc)
        self.parent: cv.ContasView = parent
        self.global_settings = Settings()
        self.settings: JanelaVisaoMensalSettings = (
            self.global_settings.load_visaomensal_settings(self.conta_dc.id)
        )

        super(VisaoGeralView, self).__init__(parent)

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle(f"Visão Mensal - (Conta {conta_dc.id})")
        self.setMinimumSize(800, 600)
        try:
            self.restoreGeometry(self.settings.dimensoes)
        except Exception as e:
            logging.error(str(e))
            self.resize(1600, 900)

        layout = QVBoxLayout()
        layout.addWidget(self.get_toolbar())

        self.splitter = QSplitter(self)
        self.splitter.addWidget(self.get_table())
        self.splitter.addWidget(self.get_lancamentos())

        try:
            splisizes: list[int] = self.settings.divisoes
        except Exception as e:
            logging.error(str(e))
            splisize = int(self.size().width() / 2)
            splisizes: list[int] = [splisize, splisize]
        finally:
            self.splitter.setSizes(splisizes)

        layout.addWidget(self.splitter)
        # layout.addWidget(self.get_toolbar())
        # layout.addWidget(self.get_table())

        self.load_table_data()

        self.setLayout(layout)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.settings.dimensoes = self.saveGeometry()
        self.settings.divisoes = self.splitter.sizes()
        return super().closeEvent(a0)

    def get_toolbar(self) -> QToolBar:
        if self.toolbar is None:
            self.toolbar = QToolBar()

            self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

            refresh_act = self.toolbar.addAction(icons.atualizar(), "Atualizar")
            refresh_act.triggered.connect(lambda: self.load_table_data())

            spacer = QWidget()
            spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.toolbar.addWidget(spacer)

            btn_exportar_planilha = self.toolbar.addAction(
                icons.exportar_planilha(), "Exportar"
            )
            btn_exportar_planilha.triggered.connect(self.on_exportar_planilha)

        return self.toolbar

    def on_exportar_planilha(self):
        datetime_str: str = moment.now().isoformat().replace(":", "_")[:19]
        default_filename: str = f"{self.conta_dc.descricao}-{datetime_str}.xlsx"
        dialog = QFileDialog()
        (filename, selectedFilter) = dialog.getSaveFileName(
            self, "Exportar planilha", default_filename
        )
        if filename is None or filename == "":
            return

        wb = Workbook()
        ws = wb.active

        column_count = self.table.columnCount()
        row_count = self.table.rowCount()

        col_titles = map(
            lambda index: self.table.horizontalHeaderItem(index).text(),
            [i for i in range(column_count)],
        )
        ws.append(list(col_titles))

        for row_index in range(row_count):
            row_values = []
            for col_index in range(column_count):
                value = ""
                cell = None
                if col_index == 0:
                    cell = self.table.itemFromIndex(
                        self.table.model().index(row_index, col_index)
                    )
                    if cell is None:
                        cell = self.table.cellWidget(row_index, col_index)
                    if cell is not None:
                        value = cell.text()
                else:
                    cell = self.table.cellWidget(row_index, col_index)
                    if cell is not None:
                        value = str_curr_to_int(cell.text()) / 100
                row_values.append(value)
            ws.append(row_values)

        wb.save(filename)

    def get_table(self):
        """Tabela de visão mensal"""
        if self.table is None:
            self.table = QTableWidget()
        return self.table

    def get_lancamentos(self):
        """Janela de descricao de lancamentos"""
        lancamentos = LancamentosView(self, self.conta_dc)
        lancamentos.changed.connect(self.handle_lancamento_changed)
        lancamentos.add_lancamento.connect(self.handle_lancamento_created)
        lancamentos.on_close.connect(self.handle_close_lancamento)
        lancamentos.on_delete.connect(self.handle_delete_lancamento)
        return lancamentos

    def handle_lancamento_changed(self):
        self.load_table_data()

    def handle_lancamento_created(self):
        self.load_table_data()

    def handle_close_lancamento(self):
        self.load_table_data()

    def handle_delete_lancamento(self):
        self.load_table_data()

    def load_table_data(self):
        self.model_visao_mensal.load()

        # unique row_labels
        self.categorias_labels = self.model_visao_mensal.get_unique_row_labels()
        self.table.setRowCount(len(self.categorias_labels) + 1)
        self.table.setColumnCount(len(self.model_visao_mensal.columns) + 1)

        for key, row_label in enumerate(self.categorias_labels):
            self.table.setItem(key, 0, QTableWidgetItem(row_label or "(vazio)"))
        self.header_labels = [col.ano_mes for col in self.model_visao_mensal.columns]
        self.header_labels.insert(0, "Categoria")
        self.table.setHorizontalHeaderLabels(self.header_labels)
        # self.table.setVerticalHeaderLabels(row_labels)

        row_index = 0
        for cell in self.model_visao_mensal.values:
            col_index = self.header_labels.index(cell.ano_mes)
            row_index = self.categorias_labels.index(cell.nm_categoria)
            # self.table.setItem(row_index, col_index, QTableWidgetItem(curr.float_to_locale(cell.valor)))
            self.table.setCellWidget(
                row_index, col_index, self.line.get_label_for_currency(cell.valor)
            )

        # TOTAL
        row_index += 1
        for key, col_label in enumerate(self.header_labels):
            if key < 1:
                self.table.setCellWidget(
                    row_index, key, self.line.get_label_for_total_text("TOTAL")
                )
                continue
            total = sum(
                [
                    cell.valor
                    for cell in self.model_visao_mensal.values
                    if cell.ano_mes == col_label
                ]
            )
            self.table.setCellWidget(
                row_index, key, self.line.get_label_for_total(total)
            )


class VisaoGeralViewLine(TableLine):
    def get_label_for_currency(self, value: int):
        label = super().get_label_for_currency(value)
        return label

    def get_label_for_total(self, value: int):
        label = super().get_label_for_currency(value)
        label.setStyleSheet(f"{label.styleSheet()}; font-weight: bold")
        return label

    def get_label_for_total_text(self, value: str):
        label = QLineEdit(value)
        label.setReadOnly(True)
        label.setFocusPolicy(Qt.NoFocus)
        label.setStyleSheet("font-weight: bold")
        return label
