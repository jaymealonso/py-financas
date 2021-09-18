import datetime
import view.icons.icons as icons
import view.contas_vw as cv
from model.Conta import Conta
from model.Lancamento import Lancamentos, Lancamento
from PyQt5.QtGui import QCloseEvent, QRegExpValidator
from PyQt5.QtCore import Qt, QObject, QRegExp, QDate
from PyQt5.QtWidgets import *
# from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QLineEdit, QPushButton, QToolBar
from util.toaster import QToaster


class LancamentosView(QWidget):
    HEADER_LABELS = [
        "ID",
        "Número Ref.",
        "Descrição",
        "Data",
        "Categorias",
        "Valor",
        "Remover"
    ]

    def __init__(self, parent: QWidget, conta_dc: Conta):
        self.toolbar: QToolBar = None
        self.table: QTableWidget = None
        self.parent: cv.ContasView = parent
        self.model_lancamentos = Lancamentos(conta_dc)
        self.conta_id = conta_dc.id

        super(LancamentosView, self).__init__()

        self.setWindowTitle(f"Lançamentos - (Conta {conta_dc.id} | {conta_dc.descricao})")
        self.setMinimumSize(800, 600)
        self.resize(1600, 900)
        layout = QVBoxLayout()
        layout.addWidget(self.get_toolbar())
        layout.addWidget(self.get_table())

        self.setLayout(layout)

    def closeEvent(self, event: QCloseEvent) -> None:
        print(f"Lancamento close event conta: {self.conta_id}")
        del self.parent.lanc_windows[str(self.conta_id)]

    def get_toolbar(self):
        self.toolbar = QToolBar()
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        save_act = self.toolbar.addAction(icons.save(), "Salvar")
        save_act.triggered.connect(lambda: self.on_save())
        self.toolbar.addSeparator()

        import_act = self.toolbar.addAction(icons.import_file(), "Importar Lançamentos")
        import_act.triggered.connect(lambda: self.on_import_lancam())

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar.addWidget(spacer)

        add_act = self.toolbar.addAction(icons.add(), "Novo Lançamento")
        add_act.triggered.connect(lambda: self.on_add_lancamento())

        return self.toolbar

    def on_import_lancam(self):
        pass

    def get_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.HEADER_LABELS))
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalHeaderLabels(self.HEADER_LABELS)
        self.load_table_data()

        return self.table

    def on_del_lancamento(self, lancamento_id: int):
        button = QMessageBox.critical(
            self,
            "Remove Lancamento?",
            f"Deseja remover o lançamento {lancamento_id} ?",
            buttons=QMessageBox.Yes | QMessageBox.No,
            defaultButton=QMessageBox.No,
        )
        if button == QMessageBox.No:
            return

        print(f"Eliminando lancamento {lancamento_id} do banco de dados ...")
        self.model_lancamentos.delete(lancamento_id)
        print("Done !!!")
        print("Reloading data...")
        self.load_table_data()
        pass

    def on_add_lancamento(self, show_message=True):
        print("Adding new lancamento in the database...")
        self.model_lancamentos.add_new(
            Lancamento(
                None,
                self.conta_id,
                'ref',
                'descr',
                datetime.date.today(),
                '0'
            )
        )
        print("Done !!!")
        print("Reloading data...")
        self.load_table_data()

        # new_index = self.table.rowCount()
        # self.table.insertRow(new_index)
        #
        # self.table.setCellWidget(new_index, 0, LancamentoTableLine.get_number_input(self))
        # self.table.setCellWidget(new_index, 4, LancamentoTableLine.get_del_button(self, new_index))
        if show_message:
            QToaster.showMessage(self, "On ADD CONTA clicked", closable=False, timeout=2000, corner=Qt.BottomRightCorner)

    def load_table_data(self):
        self.model_lancamentos.load()

        self.table.setRowCount(0)

        line = LancamentoTableLine(self)
        total_value = 0.0
        for row in self.model_lancamentos.items():
            new_index = self.table.rowCount()
            self.table.insertRow(new_index)
            # self.table.setItem(new_index, 0, QTableWidgetItem(str(row.id)))
            self.table.setItem(new_index, 1, QTableWidgetItem(row.nr_referencia))
            self.table.setItem(new_index, 2, QTableWidgetItem(row.descricao))
            # self.table.setItem(new_index, 3, QTableWidgetItem(row.data))
            self.table.setItem(new_index, 4, QTableWidgetItem("categ"))

            self.table.setCellWidget(new_index, 0, line.get_label_for_id(str(row.id)))
            # self.table.setCellWidget(new_index, 2, line.get_number_input(row.numero))
            self.table.setCellWidget(new_index, 3, line.get_date_input(row.data))
            # self.table.setCellWidget(new_index, 4, line.get_currency_input(row.value))
            self.table.setCellWidget(new_index, 5, line.get_currency_input(row.value))
            self.table.setCellWidget(new_index, 6, line.get_del_button(self, str(row.id)))
            # self.table.setCellWidget(new_index, 6, line.get_open_lanc_button(str(row.id)))

            total_value = total_value + float(row.value)

        new_index = self.table.rowCount()
        self.table.insertRow(new_index)
        self.table.setCellWidget(new_index, 0, None)
        self.table.setCellWidget(new_index, 1, None)
        self.table.setCellWidget(new_index, 5, line.get_label_for_total_curr(total_value))

        self.table.resizeColumnToContents(0)


class LancamentoTableLine(QObject):
    def __init__(self, parent: LancamentosView):
        super(QObject, self).__init__()
        self.parentOne: LancamentosView = parent

    def get_label_for_total_curr(self, value: float):
        label = QLabel(str(value))
        color = "color:darkgreen"
        if value < 0:
            color = "color:red"
        stylesheet = f"font-weight:bold;{color}"
        label.setStyleSheet(stylesheet)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return label

    def get_label_for_id(self, value: str):
        label = QLabel(value)
        label.setStyleSheet("color:red")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # label.setFlags(Qt.ItemIsEnabled)
        return label

    def get_date_input(self, date: datetime.date):
        # line_edit = QLineEdit(date)
        value = QDate(int(date[:4]), int(date[5:7]), int(date[8:10]))
        date_edit = QDateEdit(calendarPopup=True)
        date_edit.setDate(value)

        return date_edit

    def get_currency_input(self, valor: float):
        line_edit = QLineEdit()
        line_edit.setText(str(valor))
        line_edit.setAlignment(Qt.AlignRight)
        preco_validator = QRegExpValidator(QRegExp("^(\\d{1,3}(\\.\\d{3})*|(\\d+))(\\,\\d{2})?$"))
        line_edit.setValidator(preco_validator)

        return line_edit

    def get_del_button(self, parent: LancamentosView, index):
        del_pbutt = QPushButton()
        del_pbutt.setToolTip("Eliminar Conta")
        del_pbutt.setIcon(icons.delete())
        del_pbutt.clicked.connect(lambda: parent.on_del_lancamento(index))
        return del_pbutt

