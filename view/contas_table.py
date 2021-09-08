import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from util.toaster import QToaster


class ContasTab(QWidget):
    def __init__(self):
        super(ContasTab, self).__init__()
        layout = QVBoxLayout()
        layout.addWidget(self.get_toolbar())
        layout.addWidget(self.get_table())
        self.setLayout(layout)

    def get_toolbar(self):
        self.toolbar = QToolBar()
        path = os.path.dirname(os.path.abspath(__file__))
        add_act = self.toolbar.addAction(
            QIcon(QPixmap(path + r".\icons\add.png")),
            "Adicionar Conta"
        )
        add_act.triggered.connect(lambda: self.on_add_conta())
        # del_act = self.toolbar.addAction(
        #     QIcon(QPixmap(path + r".\icons\delete.png")),
        #     "Remover Conta"
        # )
        # del_act.triggered.connect(self.on_del_conta)
        return self.toolbar

    def on_add_conta(self, show_message=True):
        new_index = self.table.rowCount()
        self.table.insertRow(new_index)

        self.table.setCellWidget(new_index, 0, ContaTableLine.get_number_input(self)
        self.table.setCellWidget(new_index, 4, ContaTableLine.get_del_button(self))
        if show_message:
            QToaster.showMessage(self, "On ADD CONTA clicked", closable=False, timeout=2000, corner=Qt.BottomRightCorner)

    def on_del_conta(self):
        QToaster.showMessage(self, "On DELETE CONTA clicked", closable=False, timeout=2000, corner=Qt.BottomRightCorner)

    def get_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.on_add_conta(show_message=False)
        self.on_add_conta(show_message=False)
        # self.table.setRowCount(4)
        return self.table


class ContaTableLine:
    def __init__(self):
        pass

    @staticmethod
    def get_number_input(parent:ContasTab):
        return QLineEdit("teste")

    @staticmethod
    def get_del_button(parent:ContasTab):
        del_pbutt = QPushButton("teste")
        path = os.path.dirname(os.path.abspath(__file__))
        del_pbutt.setIcon(QIcon(QPixmap(path + r".\icons\delete.png")))
        del_pbutt.clicked.connect(parent.on_del_conta)
        return del_pbutt

