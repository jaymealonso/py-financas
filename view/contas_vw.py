import view.icons.icons as icons
import view.lanc_vw
import signal
from typing import Tuple
from PyQt5.QtCore import QObject, Qt
from PyQt5.QtGui import QIntValidator, QValidator, QCloseEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QToolBar, QTableWidget, QTableWidgetItem, QComboBox, \
   QLineEdit, QPushButton, QLabel, QMainWindow, QMessageBox
from model.Conta import ContasTipo, Contas, Conta
from util.events import subscribe, unsubscribe_refs, Eventos


class ContasView(QWidget):
    COLUMNS = {
        0: {"title": "ID", "sql_colname": "_id"},
        1: {"title": "Descrição", "sql_colname": "descricao"},
        2: {"title": "Número", "sql_colname": "numero"},
        3: {"title": "Moeda", "sql_colname": "moeda" },
        4: {"title": "Tipo", "sql_colname": "tipo"},
        5: {"title": "Total"},
        6: {"title": "Ñ classif."},
        7: {"title": "Classif."},
        8: {"title": "Remover"},
        9: {"title": "Lanç."}
    }

    def __init__(self, parent: QMainWindow):
        super(ContasView, self).__init__()

        layout = QVBoxLayout()

        self.main_window = parent
        self.toolbar: QToolBar = None
        self.table: QTableWidget = None
        self.tipos_conta: ContasTipo = ContasTipo()
        self.model_contas = Contas()
        self.lanc_windows: Tuple[view.lanc_vw.LancamentosView] = {}

        layout.addWidget(self.get_toolbar())
        layout.addWidget(self.get_table())

        self.setLayout(layout)

    def get_toolbar(self):
        self.toolbar = QToolBar()
        add_act = self.toolbar.addAction(icons.add(), "Adicionar Conta")
        add_act.triggered.connect(lambda: self.on_add_conta())
        self.toolbar.addSeparator()
        refresh_act = self.toolbar.addAction(icons.atualizar(), "Atualizar")
        refresh_act.triggered.connect(lambda: self.load_table_data())

        return self.toolbar

    def on_add_conta(self, show_message=True):
        print("Adding new conta in the database...")
        self.model_contas.add_new(Conta(None, 'nova conta', '', 'BRL', '1'))
        print("Done !!!")
        print("Reloading data...")
        self.load_table_data()

    def on_del_conta(self, conta_id: str):
        button = QMessageBox.question(
            self, "Remove conta?",
            f"Deseja remover a conta {conta_id} ?",
            buttons=QMessageBox.Yes | QMessageBox.No,
            defaultButton=QMessageBox.No,
        )
        if button == QMessageBox.No:
            return

        print(f"Eliminando conta {conta_id} do banco de dados ...")
        self.model_contas.delete(conta_id)
        print("Done !!!")
        print("Reloading data...")
        self.load_table_data()

    def on_open_lancamentos(self, conta_id: str):
        conta_dc = self.model_contas.find_by_id(conta_id)
        if conta_id not in self.lanc_windows:
            lancamentos_window = view.lanc_vw.LancamentosView(self, conta_dc)
            subscribe(Eventos.LANCAMENTO_CREATED, self.handle_lancamento_created, lancamentos_window)
            subscribe(Eventos.LANCAMENTO_WINDOW_CLOSED, self.handle_close_lancamento, lancamentos_window)
            self.lanc_windows[conta_id] = lancamentos_window
        else:
            lancamentos_window = self.lanc_windows[conta_id]

        if lancamentos_window.isHidden():
            position = self.main_window.pos()
            position.setX(position.x() + (50 * len(self.lanc_windows)))
            position.setY(position.y() + (50 * len(self.lanc_windows)))
            print(f"> Abrir janela Lanç. (conta id:{conta_id}) posição (X: {position.x()}, Y: {position.y()}).")
            lancamentos_window.move(position)

            lancamentos_window.show()

        lancamentos_window.activateWindow()

    def handle_close_lancamento(self, conta_id: str):
        print(f"Lancamento close event UNSUBSCRIBE conta: {conta_id}")
        unsubscribe_refs(self.lanc_windows[conta_id])
        del self.lanc_windows[conta_id]

    def handle_lancamento_created(self, lancamento):
        print(f"Lancamento criado {lancamento.id}, recarregando dados na contas view.")
        self.load_table_data()

    def get_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.COLUMNS))
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalHeaderLabels([col["title"] for col in self.COLUMNS.values()])
        self.load_table_data()

        return self.table

    def table_cell_changed(self, row: int, col: int):
        conta_dc = self.model_contas.items()[row]
        item = self.table.item(row, col)
        column_data = self.COLUMNS.get(col)

        print(f"Modificando conta numero:{conta_dc.id} campo \"{column_data['sql_colname']}\" para valor \"{item.text()}\"")
        conta_dc.__setattr__(column_data["sql_colname"], item.text())
        self.model_contas.update(conta_dc)

    def load_table_data(self):
        try:
            print("> Disconnecting table cellChanged... ", end=" ")
            self.table.cellChanged.disconnect()
            print("Disconnected!")
        except:
            print("Cellchanged not connected!")

        print("Loading contas data...")
        self.model_contas.load()

        # Limpa a tabela
        self.table.setRowCount(0)

        line = ContaTableLine(self)

        print("Preenchendo dados na tabela.")
        for row in self.model_contas.items():
            new_index = self.table.rowCount()
            self.table.insertRow(new_index)

            # self.table.setItem(new_index, 0, QTableWidgetItem(str(row.id)))
            self.table.setCellWidget(new_index, 0, line.get_label_for_id(str(row.id)))
            self.table.setItem(new_index, 1, QTableWidgetItem(row.descricao))
            # self.table.setCellWidget(new_index, 2, line.get_number_input(row.numero))
            self.table.setItem(new_index, 2, QTableWidgetItem(row.numero))
            self.table.setItem(new_index, 3, QTableWidgetItem(row.moeda))
            # self.table.setItem(new_index, 4, QTableWidgetItem(self.tipos_conta.getByKey(row.tipo_id).descricao))
            self.table.setCellWidget(new_index, 4, line.get_tipo_conta_dropdown(row))
            self.table.setCellWidget(new_index, 5, line.get_label_for_total_curr(row.total))
            self.table.setCellWidget(new_index, 6, line.get_label_for_n_class(str(row.lanc_n_class)))
            self.table.setCellWidget(new_index, 7, line.get_label_for_classif(str(row.lanc_classif)))
            self.table.setCellWidget(new_index, 8, line.get_del_button(str(row.id)))
            self.table.setCellWidget(new_index, 9, line.get_open_lanc_button(str(row.id)))

        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(1)
        self.table.resizeColumnToContents(2)
        self.table.resizeColumnToContents(3)
        self.table.resizeColumnToContents(4)
        self.table.setColumnWidth(6, 140)
        self.table.setColumnWidth(7, 140)
        self.table.setColumnWidth(8, 100)
        self.table.setColumnWidth(9, 100)

        self.table.cellChanged.connect(self.table_cell_changed)
        print("> Cellchanged connected again!")

        # self.table.resizeColumnToContents(6)
        # self.table.resizeColumnToContents(7)

#         numericD = NumericDelegate(self.table)
#         self.table.setItemDelegate(numericD)
#
#
# class NumericDelegate(QStyledItemDelegate):
#     def createEditor(self, parent, option, index):
#         editor = super(NumericDelegate, self).createEditor(parent, option, index)
#         print("numeric delegate is QlineEdit:", isinstance(editor, QLineEdit))
#         if isinstance(editor, QLineEdit):
#             reg_ex = QRegExp("[0-9]+.?[0-9]{,2}")
#             validator = QRegExpValidator(reg_ex, editor)
#             editor.setValidator(validator)
#         return editor


class ContaTableLine(QObject):
    def __init__(self, parent: ContasView):
        super(QObject, self).__init__()
        self.parentOne: ContasView = parent

    def get_label_for_id(self, value: str):
        label = QLabel(value)
        label.setStyleSheet("color:red")
        label.setAlignment(Qt.AlignCenter)
        # label.setFlags(Qt.ItemIsEnabled)
        return label

    def get_label_for_n_class(self, value: str):
        label = QLabel(value)
        label.setStyleSheet("color:red;font-weight:bold")
        label.setAlignment(Qt.AlignCenter)
        return label

    def get_label_for_classif(self, value: str):
        label = QLabel(value)
        label.setStyleSheet("color:darkgreen;font-weight:bold")
        label.setAlignment(Qt.AlignCenter)
        return label

    def get_label_for_total_curr(self, value: float):
        label = QLabel(str(value))
        color = "color:darkgreen"
        if value < 0:
            color = "color:red"
        stylesheet = f"margin-right:3px; margin-left:3px; font-weight:bold;{color}"
        label.setStyleSheet(stylesheet)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return label

    def get_number_input(self, numero:int):
        line_edit = QLineEdit()
        line_edit.setText(str(numero))
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

    def get_tipo_conta_dropdown(self, conta: Conta):
        combobox = QComboBox()
        index: int = 0
        # for tipo_conta in self.parentOne.tipos_conta.items():
        items = self.parentOne.tipos_conta.items()
        for key, item_index in enumerate(items):
            item = items.get(item_index)
            if item.id == conta.tipo_id:
                index = key
            combobox.addItem(item.descricao, item.id)

        combobox.setCurrentIndex(index)
        combobox.currentIndexChanged.connect(lambda: self.tipo_conta_dropdown_change(combobox, conta))
        return combobox

    def tipo_conta_dropdown_change(self, combobox: QComboBox, conta: Conta):
        data = combobox.currentData()
        conta.tipo_id = data
        self.parentOne.model_contas.update(conta)

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

