import view.icons.icons as icons
import view.lanc_vw
from PyQt5.QtCore import QObject, Qt, QRegExp
from PyQt5.QtGui import QIntValidator, QValidator, QRegExpValidator
from PyQt5.QtWidgets import *
# from PyQt5.QtWidgets import QWidget, QVBoxLayout, \
#    QToolBar, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QPushButton, *
from model.Conta import ContasTipo, Contas, Conta


class ContasView(QWidget):
    HEADER_LABELS = [
        "ID",
        "Descrição",
        "Número",
        "Moeda",
        "Tipo",
        "Remover",
        "Lanç."
    ]

    def __init__(self):
        super(ContasView, self).__init__()

        layout = QVBoxLayout()

        self.toolbar: QToolBar = None
        self.table: QTableWidget = None
        self.tipos_conta: ContasTipo = ContasTipo()
        self.model_contas = Contas()
        self.lanc_windows = {}

        layout.addWidget(self.get_toolbar())
        layout.addWidget(self.get_table())

        self.setLayout(layout)

    def get_toolbar(self):
        self.toolbar = QToolBar()
        add_act = self.toolbar.addAction(icons.add(), "Adicionar Conta")
        add_act.triggered.connect(lambda: self.on_add_conta())

        return self.toolbar

    def on_add_conta(self, show_message=True):
        print("Adding new conta in the database...")
        self.model_contas.add_new(Conta(None, 'nova conta', '', 'BRL', '1'))
        print("Done !!!")
        print("Reloading data...")
        self.load_table_data()

    def on_del_conta(self, conta_id: str):
        print(f"Eliminando conta {conta_id} do banco de dados ...")
        self.model_contas.delete(conta_id)
        print("Done !!!")
        print("Reloading data...")
        self.load_table_data()

    def on_open_lancamentos(self, conta_id: str):
        if conta_id not in self.lanc_windows:
            lancamentos_window = view.lanc_vw.LancamentosView(self, conta_id)
            self.lanc_windows[conta_id] = lancamentos_window
        else:
            lancamentos_window = self.lanc_windows[conta_id]

        if lancamentos_window.isHidden():
            position = self.pos()
            print(f"> Open window Position X: {position.x()}, Y:{position.y()}.")
            position.setX(position.x() + (50 * len(self.lanc_windows)))
            position.setY(position.y() + (50 * len(self.lanc_windows)))
            lancamentos_window.move(position)

            lancamentos_window.show()

        lancamentos_window.activateWindow()

    def get_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.HEADER_LABELS))
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalHeaderLabels(self.HEADER_LABELS)
        # self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.load_table_data()

        return self.table

    def load_table_data(self):
        model_contas = Contas()
        model_contas.load()

        # Limpa a tabela
        self.table.setRowCount(0)

        for row in model_contas.items():
            new_index = self.table.rowCount()
            self.table.insertRow(new_index)
            # self.table.setItem(new_index, 0, QTableWidgetItem(str(row.id)))
            self.table.setItem(new_index, 1, QTableWidgetItem(row.descricao))
            self.table.setItem(new_index, 2, QTableWidgetItem(row.numero))
            self.table.setItem(new_index, 3, QTableWidgetItem(row.moeda))
            self.table.setItem(new_index, 4, QTableWidgetItem(self.tipos_conta.getByKey(row.tipo_id).descricao))

            line = ContaTableLine(self)

            self.table.setCellWidget(new_index, 0, line.get_label(str(row.id)))
            # self.table.setCellWidget(new_index, 2, line.get_number_input(row.numero))
            # self.table.setCellWidget(new_index, 4, line.get_tipo_conta_dropdown(row.tipo_id))
            self.table.setCellWidget(new_index, 5, line.get_del_button(str(row.id)))
            self.table.setCellWidget(new_index, 6, line.get_open_lanc_button(str(row.id)))

        self.table.resizeColumnsToContents()
        numericD = NumericDelegate(self.table)
        self.table.setItemDelegate(numericD)


class NumericDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = super(NumericDelegate, self).createEditor(parent, option, index)
        print("numeric delegate is QlineEdit:", isinstance(editor, QLineEdit))
        if isinstance(editor, QLineEdit):
            reg_ex = QRegExp("[0-9]+.?[0-9]{,2}")
            validator = QRegExpValidator(reg_ex, editor)
            editor.setValidator(validator)
        return editor

class ContaTableLine(QObject):
    def __init__(self, parent: ContasView):
        super(QObject, self).__init__()
        self.parentOne: ContasView = parent

    def get_label(self, value: str):
        label = QLabel(value)
        label.setStyleSheet("color:red")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # label.setFlags(Qt.ItemIsEnabled)
        return label

    def get_number_input(self, numero:int):
        line_edit = QLineEdit()
        line_edit.setText(numero)
        line_edit.setValidator(QIntValidator())
        line_edit.textChanged.connect(self.check_state)
        line_edit.textChanged.emit(line_edit.text())

        return line_edit

    def check_state(self, *args, **kwargs):
        print("entered validator", args[0])
        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QValidator.Acceptable:
            color = '#c4df9b'  # green
        elif state == QValidator.Intermediate:
            color = '#fff79a'  # yellow
        else:
            color = '#f6989d'  # red
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)

    def get_tipo_conta_dropdown(self, tipo_id:str):
        combobox = QComboBox()
        index: int
        for key, item in enumerate(self.parentOne.tipos_conta.items()):
            if item.id == tipo_id:
                index = key
            combobox.addItem(item.descricao, item.id)

        combobox.setCurrentIndex(index)
        return combobox

    def get_del_button(self, conta_id: str):
        del_pbutt = QPushButton()
        del_pbutt.setToolTip("Eliminar Conta")
        del_pbutt.setIcon(icons.delete())
        del_pbutt.clicked.connect(lambda: self.parentOne.on_del_conta(conta_id))
        return del_pbutt

    def get_open_lanc_button(self, conta_id: str):
        op_lanc_pbutt = QPushButton()
        op_lanc_pbutt.setToolTip("Abrir Lançamentos")
        op_lanc_pbutt.setIcon(icons.open_lancamentos())
        op_lanc_pbutt.clicked.connect(lambda: self.parentOne.on_open_lancamentos(conta_id))
        return op_lanc_pbutt

