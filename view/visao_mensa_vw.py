import view.contas_vw as cv
from model.Conta import Conta
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QLineEdit, QPushButton, QToolBar, QSizePolicy, \
    QMessageBox, QTableWidgetItem, QLabel, QComboBox, QDateEdit
from util.settings import Settings
from model.VisaoMensal import VisaoMensal


class VisaoGeralView(QWidget):
    def __init__(self, parent: QWidget, conta_dc: Conta):
        self.toolbar = QToolBar()
        self.table = QTableWidget()
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
        self.table.verticalHeader().setVisible(False)
        self.load_table_data()

        return self.table

    def load_table_data(self):
        self.model_visao_mensal.load()

        self.table.setColumnCount(len(self.model_visao_mensal.columns))
        header_labels = [col[1] for col in self.model_visao_mensal.columns]
        self.table.setHorizontalHeaderLabels(header_labels)
        # for col in self.model_visao_mensal.columns:
        #     for cell in self.model_visao_mensal.values if cell[0] == col[0]:
        #         self.table.insertRow(new_index)
        #         self.table.setItem(new_index, 1, QTableWidgetItem(row.nr_referencia))


