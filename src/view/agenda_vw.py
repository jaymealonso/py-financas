import view.icons.icons as icons
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QLineEdit,
    QPushButton,
)
from lib import CustomToolbar
from util.toaster import QToaster


class AgendaView(QWidget):
    def __init__(self):
        super(AgendaView, self).__init__()

        self.toolbar = self.get_toolbar()
        self.table: QTableWidget = self.get_table()

        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def get_toolbar(self) -> CustomToolbar:
        toolbar = CustomToolbar()
        add_act = toolbar.addAction(icons.add(), "Adicionar Compromisso")
        add_act.triggered.connect(lambda: self.on_add_compromisso())
        return toolbar

    def on_add_conta(self, show_message=True):
        new_index = self.table.rowCount()
        self.table.insertRow(new_index)

        self.table.setCellWidget(new_index, 0, AgendaTabLine.get_number_input(self))
        self.table.setCellWidget(new_index, 4, AgendaTabLine.get_del_button(self))
        if show_message:
            QToaster.showMessage(self, "On ADD CONTA clicked")

    def on_add_compromisso(self, show_message=True):
        new_index = self.table.rowCount()
        self.table.insertRow(new_index)

        self.table.setCellWidget(new_index, 0, AgendaTabLine.get_number_input(self))
        self.table.setCellWidget(
            new_index, 4, AgendaTabLine.get_del_button(self, new_index)
        )
        if show_message:
            QToaster.showMessage(self, "On ADD COMPROMISSO clicked")

    def on_del_compromisso(self, index):
        self.table.removeRow(index)
        QToaster.showMessage(self,
            f"On DELETE CONTA index:{index} clicked")

    def get_table(self) -> QTableWidget:
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.on_add_compromisso(show_message=False)
        self.on_add_compromisso(show_message=False)
        return self.table


class AgendaTabLine:
    def __init__(self):
        pass

    @staticmethod
    def get_number_input(parent: AgendaView):
        return QLineEdit("teste")

    @staticmethod
    def get_del_button(parent: AgendaView, index):
        del_pbutt = QPushButton()
        del_pbutt.setToolTip("Eliminar Conta")
        del_pbutt.setIcon(icons.delete())
        del_pbutt.clicked.connect(lambda: parent.on_del_compromisso(index))
        return del_pbutt
