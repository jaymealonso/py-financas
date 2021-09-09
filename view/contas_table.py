import view.icons.icons as icons
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from util.toaster import QToaster


class ContasTab(QWidget):
    def __init__(self):
        super(ContasTab, self).__init__()

        layout = QVBoxLayout()

        self.toolbar:QToolBar = None
        self.table:QTableWidget = None
        layout.addWidget(self.get_toolbar())
        layout.addWidget(self.get_table())

        self.setLayout(layout)

    def get_toolbar(self):
        self.toolbar = QToolBar()
        add_act = self.toolbar.addAction(icons.add(),"Adicionar Conta")
        add_act.triggered.connect(lambda: self.on_add_conta())

        return self.toolbar

    def on_add_conta(self, show_message=True):
        new_index = self.table.rowCount()
        self.table.insertRow(new_index)

        self.table.setCellWidget(new_index, 0, ContaTableLine.get_number_input(self))
        self.table.setCellWidget(new_index, 4, ContaTableLine.get_del_button(self, new_index))
        if show_message:
            QToaster.showMessage(self, "On ADD CONTA clicked", closable=False, timeout=2000, corner=Qt.BottomRightCorner)

    def on_del_conta(self, index):
        self.table.removeRow(index)
        QToaster.showMessage(self, f"On DELETE CONTA index:{index} clicked", closable=False, timeout=2000, corner=Qt.BottomRightCorner)

    def get_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.on_add_conta(show_message=False)
        self.on_add_conta(show_message=False)

        return self.table


class ContaTableLine:
    def __init__(self):
        pass

    @staticmethod
    def get_number_input(parent:ContasTab):
        return QLineEdit("teste")

    @staticmethod
    def get_del_button(parent:ContasTab, index):
        del_pbutt = QPushButton()
        del_pbutt.setToolTip("Eliminar Conta")
        del_pbutt.setIcon(icons.delete())
        del_pbutt.clicked.connect(lambda: parent.on_del_conta(index))
        return del_pbutt

