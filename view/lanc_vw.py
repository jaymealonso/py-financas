import view.icons.icons as icons
import view.contas_vw as cv
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QLineEdit, QPushButton, QToolBar
from util.toaster import QToaster


class LancamentosView(QWidget):
    def __init__(self, parent: QWidget, conta_id: str):
        self.toolbar: QToolBar = None
        self.table: QTableWidget = None
        self.parent:cv.ContasView = parent
        self.conta_id = conta_id

        super(LancamentosView, self).__init__()

        self.setMinimumSize(800, 600)
        self.resize(1600, 900)
        layout = QVBoxLayout()
        layout.addWidget(self.get_toolbar())
        layout.addWidget(self.get_table())

        self.setLayout(layout)

    def closeEvent(self, event: QCloseEvent) -> None:
        del self.parent.lanc_windows[self.conta_id]
        print(f"Lancamento close event conta:{self.conta_id}")

    def get_toolbar(self):
        self.toolbar = QToolBar()
        add_act = self.toolbar.addAction(icons.add(), "Novo Lançamento")
        add_act.triggered.connect(lambda: self.on_add_lancam())
        self.toolbar.addSeparator()
        import_act = self.toolbar.addAction(icons.import_file(), "Importar Lançamentos")
        import_act.triggered.connect(lambda: self.on_import_lancam())

        return self.toolbar

    def on_add_lancam(self):
        pass

    def on_import_lancam(self):
        pass

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
    def get_number_input(parent:LancamentosView):
        return QLineEdit("teste")

    @staticmethod
    def get_del_button(parent:LancamentosView, index):
        del_pbutt = QPushButton()
        del_pbutt.setToolTip("Eliminar Conta")
        del_pbutt.setIcon(icons.delete())
        del_pbutt.clicked.connect(lambda: parent.on_del_conta(index))
        return del_pbutt

