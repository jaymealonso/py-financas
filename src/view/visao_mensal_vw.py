from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QToolBar, QTableWidgetItem, QLabel, QDialog
from util.settings import Settings

import view.contas_vw as cv
import util.curr_formatter as curr
from view.TableLine import TableLine
from model.Conta import Conta
from model.VisaoMensal import VisaoMensal


class VisaoGeralView(QDialog):
    def __init__(self, parent: QWidget, conta_dc: Conta):
        self.toolbar = QToolBar()
        self.table = QTableWidget()
        self.line = VisaoGeralViewLine()
        self.conta_dc = conta_dc
        self.model_visao_mensal = VisaoMensal(self.conta_dc)
        self.parent: cv.ContasView = parent
        self.settings = Settings()

        super(VisaoGeralView, self).__init__(parent)

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
        categorias_labels = self.model_visao_mensal.get_unique_row_labels()
        self.table.setRowCount(len(categorias_labels) + 1)
        self.table.setColumnCount(len(self.model_visao_mensal.columns) + 1)

        for key, row_label in enumerate(categorias_labels):
            self.table.setItem(key, 0, QTableWidgetItem(row_label or "(vazio)"))
        header_labels = [col.ano_mes for col in self.model_visao_mensal.columns]
        header_labels.insert(0, "Categoria")
        self.table.setHorizontalHeaderLabels(header_labels)
        # self.table.setVerticalHeaderLabels(row_labels)

        row_index = 0
        for cell in self.model_visao_mensal.values:
            col_index = header_labels.index(cell.ano_mes)
            row_index = categorias_labels.index(cell.nm_categoria)
            # self.table.setItem(row_index, col_index, QTableWidgetItem(curr.float_to_locale(cell.valor)))
            self.table.setCellWidget(row_index, col_index, self.line.get_label_for_currency(cell.valor))

        # TOTAL
        row_index += 1
        for key, col_label in enumerate(header_labels):
            if key < 1:
                self.table.setCellWidget(row_index, key, self.line.get_label_for_total_text("TOTAL"))
                continue
            total = sum([cell.valor for cell in self.model_visao_mensal.values if cell.ano_mes == col_label])
            self.table.setCellWidget(row_index, key, self.line.get_label_for_total(total))


class VisaoGeralViewLine(TableLine):
    def get_label_for_currency(self, value: int):
        label = super().get_label_for_currency(value)
        return label

    def get_label_for_total(self, value: int):
        label = super().get_label_for_currency(value)
        label.setStyleSheet(f"{label.styleSheet()}; font-weight: bold")
        return label

    def get_label_for_total_text(self, value: str):
        label = QLabel(value)
        label.setStyleSheet("font-weight: bold")
        return label



