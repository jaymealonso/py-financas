from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QToolBar, QTableWidgetItem, QLabel
from util.settings import Settings

import view.contas_vw as cv
import util.curr_formatter as curr
from view.TableLine import TableLine
from model.Conta import Conta
from model.VisaoMensal import VisaoMensal


class VisaoGeralView(QWidget):
    def __init__(self, parent: QWidget, conta_dc: Conta):
        self.toolbar = QToolBar()
        self.table = QTableWidget()
        self.line = VisaoGeralViewLine()
        self.conta_dc = conta_dc
        self.model_visao_mensal = VisaoMensal(self.conta_dc)
        self.parent: cv.ContasView = parent
        self.settings = Settings()

        super(VisaoGeralView, self).__init__()

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle(f"Visão Mensal - (Conta {conta_dc.id})")
        self.setMinimumSize(800, 600)
        self.resize(1600, 900)

        layout = QVBoxLayout()
        layout.addWidget(self.get_table())

        self.setLayout(layout)

    def get_table(self):
        self.load_table_data()

        return self.table

    def load_table_data(self):
        self.model_visao_mensal.load()

        # unique row_labels
        row_labels = self.model_visao_mensal.get_unique_row_labels()
        self.table.setRowCount(len(row_labels))
        for key, row_label in enumerate(row_labels):
            self.table.setItem(key, 0, QTableWidgetItem(row_label or "(vazio)"))

        self.table.setColumnCount(len(self.model_visao_mensal.columns))
        header_labels = [col.ano_mes for col in self.model_visao_mensal.columns]
        self.table.setHorizontalHeaderLabels(header_labels)
        self.table.setVerticalHeaderLabels(row_labels)

        for cell in self.model_visao_mensal.values:
            col_index = header_labels.index(cell.ano_mes)
            row_index = row_labels.index(cell.nm_categoria)
            # self.table.setItem(row_index, col_index, QTableWidgetItem(curr.float_to_locale(cell.valor)))
            self.table.setCellWidget(row_index, col_index, self.line.get_label_for_currency(cell.valor))


class VisaoGeralViewLine(TableLine):
    def get_label_for_currency(self, value: float):
        label = super().get_label_for_currency(value)
        return label




