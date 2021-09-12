import view.icons.icons as icons
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from util.toaster import QToaster


class LancamentosTab(QWidget):
    def __init__(self):
        super(LancamentosTab, self).__init__()

        layout = QVBoxLayout()

        self.table:QTableWidget = None
        layout.addWidget(self.get_table())

        self.setLayout(layout)

    def get_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.on_add_lancamento(show_message=False)
        self.on_add_lancamento(show_message=False)

        return self.table

    def on_add_lancamento(self, show_message=True):
        new_index = self.table.rowCount()
        self.table.insertRow(new_index)

        self.table.setCellWidget(new_index, 0, LancamentoTableLine.get_number_input(self))
        self.table.setCellWidget(new_index, 4, LancamentoTableLine.get_del_button(self, new_index))
        if show_message:
            QToaster.showMessage(self, "On ADD CONTA clicked", closable=False, timeout=2000, corner=Qt.BottomRightCorner)


class LancamentoTableLine:
    def __init__(self):
        pass

    @staticmethod
    def get_number_input(parent:LancamentosTab):
        return QLineEdit("teste")

    @staticmethod
    def get_del_button(parent:LancamentosTab, index):
        del_pbutt = QPushButton()
        del_pbutt.setToolTip("Eliminar Conta")
        del_pbutt.setIcon(icons.delete())
        del_pbutt.clicked.connect(lambda: parent.on_del_conta(index))
        return del_pbutt