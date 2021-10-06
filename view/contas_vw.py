import view.icons.icons as icons
import view.lanc_vw
from view.TableLine import TableLine
from view.visao_mensal_vw import VisaoGeralView
from typing import Tuple
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QValidator, QCursor, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QToolBar, QComboBox, QLineEdit, QPushButton, QMainWindow, \
    QMessageBox, QApplication, QTableView
from model.Conta import ContasTipo, Contas, Conta
from util.events import subscribe, unsubscribe_refs, Eventos
from util.custom_component import ComboBoxDelegate


class ContasView(QWidget):
    COLUMNS = {
        0: {"title": "ID", "sql_colname": "_id"},
        1: {"title": "Descrição", "sql_colname": "descricao"},
        2: {"title": "Número", "sql_colname": "numero"},
        3: {"title": "Moeda", "sql_colname": "moeda" },
        4: {"title": "Tipo", "sql_colname": "tipo_id"},
        5: {"title": "Total"},
        6: {"title": "Ñ classif."},
        7: {"title": "Classif."},
        8: {"title": "Remover"},
        9: {"title": "Lanç."},
        10: {"title": "Vis. Mensal"}
    }

    def __init__(self, parent: QMainWindow):
        super(ContasView, self).__init__()

        layout = QVBoxLayout()

        self.main_window = parent
        self.toolbar = QToolBar()
        self.table = QTableView()
        self.model_tps_conta: ContasTipo = ContasTipo()
        self.model_contas = Contas()
        self.lanc_windows: Tuple[view.lanc_vw.LancamentosView] = {}
        self.visao_geral_window = None

        layout.addWidget(self.get_toolbar())
        layout.addWidget(self.get_table())

        self.setLayout(layout)
        self.on_open_lancamentos("5")

    def get_toolbar(self):
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
            print(f"> Abrir janela Lanç. (conta id:{conta_id}) posição (X: {position.x()}, Y: {position.y()}).")

            lancamentos_window.show()

        lancamentos_window.activateWindow()

    def on_open_visao_mensal(self, conta_id: str):
        conta_items = self.model_contas.items()
        conta = [x for x in conta_items if x.id == int(conta_id)]
        self.visao_geral_window = VisaoGeralView(self, conta[0])
        self.visao_geral_window.show()

    def handle_close_lancamento(self, conta_id: str):
        print(f"Lancamento close event UNSUBSCRIBE conta: {conta_id}")
        unsubscribe_refs(self.lanc_windows[conta_id])
        del self.lanc_windows[conta_id]

    def handle_lancamento_created(self, lancamento):
        print(f"Lancamento criado {lancamento.id}, recarregando dados na contas view.")
        self.load_table_data()

    def get_table(self):
        model = QStandardItemModel(0, len(self.COLUMNS))
        model.setHorizontalHeaderLabels([col["title"] for col in self.COLUMNS.values()])
        self.table.setModel(model)
        self.table.verticalHeader().setVisible(False)
        self.load_table_data()

        return self.table

    # def table_cell_changed(self, row: int, col: int):
    def model_item_changed(self, item):
        conta_dc = self.model_contas.items()[item.row()]
        column_data = self.COLUMNS.get(item.column())

        print(f"Modificando conta numero:{conta_dc.id} campo \"{column_data['sql_colname']}\" para valor \"{item.text()}\"")
        conta_dc.__setattr__(column_data["sql_colname"], item.text())
        self.model_contas.update(conta_dc)

    def load_table_data(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        model = self.table.model()
        try:
            print("> Disconnecting model.itemChanged ... ", end=" ")
            model.itemChanged.disconnect()
            print("Disconnected!")
        except:
            print("was not connected!")

        print("Loading contas data...")
        self.model_contas.load()

        # Limpa a tabela
        model.setRowCount(0)

        line = ContaTableLine(self)

        self.table.setItemDelegateForColumn(4, line.get_tipo_conta_dropdown_delegate())

        rows = self.model_contas.items()

        print("Preenchendo dados na tabela.")
        for row in rows:
            new_index = model.rowCount()
            model.insertRow(new_index)

            self.table.setIndexWidget(model.index(new_index, 0),
                                      line.get_label_for_id(str(row.id)))

            model.setItem(new_index, 1, QStandardItem(row.descricao))
            model.setItem(new_index, 2, QStandardItem(row.numero))
            model.setItem(new_index, 3, QStandardItem(row.moeda))

            model.setItemData(model.index(new_index, 4), {0: row.tipo_id})

            self.table.setIndexWidget(model.index(new_index, 5), line.get_label_for_total_curr(row.total))
            self.table.setIndexWidget(model.index(new_index, 6), line.get_label_for_n_class(row.lanc_n_class))
            self.table.setIndexWidget(model.index(new_index, 7), line.get_label_for_classif(row.lanc_classif))
            self.table.setIndexWidget(model.index(new_index, 8), line.get_del_button(str(row.id)))
            self.table.setIndexWidget(model.index(new_index, 9), line.get_open_lanc_button(str(row.id)))
            self.table.setIndexWidget(model.index(new_index, 10), line.get_visao_mensal(str(row.id)))

        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(1)
        self.table.resizeColumnToContents(2)
        self.table.resizeColumnToContents(3)
        self.table.setColumnWidth(4, 260)
        self.table.setColumnWidth(6, 120)
        self.table.setColumnWidth(7, 120)
        self.table.setColumnWidth(8, 100)
        self.table.setColumnWidth(9, 100)
        self.table.setColumnWidth(10, 130)

        model.itemChanged.connect(self.model_item_changed)
        print("> itemChanged connected again!")
        QApplication.restoreOverrideCursor()


class ContaTableLine(TableLine):
    def __init__(self, parent: ContasView):
        super(TableLine, self).__init__()
        self.parentOne: ContasView = parent

    def get_label_for_n_class(self, value: int):
        label = super().get_label_for_integer(value)
        label.setStyleSheet("color:red;font-weight:bold")
        return label

    def get_label_for_classif(self, value: int):
        label = super().get_label_for_integer(value)
        label.setStyleSheet("color:darkgreen;font-weight:bold")
        return label

    def get_label_for_total_curr(self, value: float):
        label = super().get_label_for_currency(value)
        color = "color:darkgreen"
        if value < 0:
            color = "color:red"
        stylesheet = f"margin-right:3px; margin-left:3px; font-weight:bold;{color}"
        label.setStyleSheet(stylesheet)
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

    def get_tipo_conta_dropdown_delegate(self):
        tipos_conta = {}
        for item in self.parentOne.model_tps_conta.items():
            tipos_conta[item.id] = item.descricao

        cmb_delegate = ComboBoxDelegate(tipos_conta, self.parentOne.table)

        return cmb_delegate

    def get_tipo_conta_dropdown(self, conta: Conta):
        combobox = QComboBox()
        index: int = 0
        # for tipo_conta in self.parentOne.tipos_conta.items():
        items = self.parentOne.model_tps_conta.items()
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

    def get_visao_mensal(self, conta_id: str):
        op_lanc_pbutt = QPushButton()
        op_lanc_pbutt.setToolTip("Abrir Visão Mensal")
        op_lanc_pbutt.setIcon(icons.visao_mensal())
        op_lanc_pbutt.clicked.connect(lambda: self.parentOne.on_open_visao_mensal(conta_id))
        return op_lanc_pbutt
