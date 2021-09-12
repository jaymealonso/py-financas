import view.icons.icons as icons
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from util.toaster import QToaster
from model.Conta import ContasTipo, Contas


class ContasTab(QWidget):
    HEADER_LABELS = [
        "ID",
        "Descrição",
        "Número",
        "Moeda",
        "Tipo",
        "Remover"
    ]

    def __init__(self):
        super(ContasTab, self).__init__()

        layout = QVBoxLayout()

        self.toolbar: QToolBar = None
        self.table: QTableWidget = None
        self.tipos_conta: ContasTipo = ContasTipo()
        self.model_contas = Contas()

        layout.addWidget(self.get_toolbar())
        layout.addWidget(self.get_table())

        self.setLayout(layout)

    def get_toolbar(self):
        self.toolbar = QToolBar()
        add_act = self.toolbar.addAction(icons.add(), "Adicionar Conta")
        add_act.triggered.connect(lambda: self.on_add_conta())

        return self.toolbar

    def on_add_conta(self, show_message=True):
        new_index = self.table.rowCount()
        self.table.insertRow(new_index)

        self.table.setCellWidget(new_index, 0, ContaTableLine.get_number_input(self))
        self.table.setCellWidget(new_index, 4, ContaTableLine.get_tipo_conta_dropdown(self))
        self.table.setCellWidget(new_index, 5, ContaTableLine.get_del_button(self))
        if show_message:
            QToaster.showMessage(self, "On ADD CONTA clicked", closable=False, timeout=2000, corner=Qt.BottomRightCorner)

    def on_del_conta(self, button: QPushButton):
        cell = button.parent()
        row_no = self.table.row(cell)
        self.table.removeRow(row_no)
        QToaster.showMessage(self, f"On DELETE CONTA index:{row_no} clicked", closable=False, timeout=2000, corner=Qt.BottomRightCorner)

    def get_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.HEADER_LABELS))
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalHeaderLabels(self.HEADER_LABELS)
        self.load_table_data()

        return self.table

    def load_table_data(self):
        model_contas = Contas()
        model_contas.load()

        for row in model_contas.items():
            new_index = self.table.rowCount()
            self.table.insertRow(new_index)
            self.table.setItem(new_index, 0, QTableWidgetItem(str(row.id)))
            self.table.setItem(new_index, 1, QTableWidgetItem(row.descricao))
            self.table.setItem(new_index, 2, QTableWidgetItem(row.numero))
            self.table.setItem(new_index, 3, QTableWidgetItem(row.moeda))
            # self.table.setItem(new_index, 4, QTableWidgetItem(row.tipo_id))

            self.table.setCellWidget(new_index, 4, ContaTableLine.get_tipo_conta_dropdown(self, row.tipo_id) )
            self.table.setCellWidget(new_index, 5, ContaTableLine.get_del_button(self))


class ContaTableLine:
    @staticmethod
    def get_number_input(parent:ContasTab):
        return QLineEdit("teste")

    @staticmethod
    def get_tipo_conta_dropdown(parent: ContasTab, tipo_id:str):
        combobox = QComboBox()
        index: int
        for key, item in enumerate(parent.tipos_conta.items()):
            if item.id == tipo_id:
                index = key
            combobox.addItem(item.descricao, item.id)

        combobox.setCurrentIndex(index)
        return combobox

    @staticmethod
    def get_del_button(parent: ContasTab):
        del_pbutt = QPushButton()
        del_pbutt.setToolTip("Eliminar Conta")
        del_pbutt.setIcon(icons.delete())
        del_pbutt.clicked.connect(lambda: parent.on_del_conta(del_pbutt))
        return del_pbutt

