from enum import StrEnum, IntEnum, auto

import view.icons.icons as icons
import view.lanc_vw
from lib.Genericos.log import logging
import util.curr_formatter as curr
from lib.Genericos.TableLine import TableLine
from view.visao_mensal_vw import VisaoGeralView
from typing import Tuple
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import (
    QIntValidator,
    QValidator,
    QCursor,
    QStandardItemModel,
)
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QComboBox,
    QLineEdit,
    QPushButton,
    QMainWindow,
    QMessageBox,
    QApplication,
    QTableView,
)
from lib import CustomToolbar
from model import ContasTipo, Contas, Conta, ORMLancamentos
from util import (
    ButtonDelegate,
    GenericInputDelegate,
    ComboBoxDelegate,
    IDLabelDelegate,
    CurrencyLabelDelegate,    
)


class TEXTS(StrEnum):
    ADD_ACCOUNT_BTN_TEXT = "Adicionar Conta"
    REFRESH = "Atualizar"
    REMOVE_ACCOUNT_TITLE = "Remove conta?"
    REMOVE_ACCOUNT_QUESTION = "Deseja remover a conta {0} ?"
    REMOVE_ACCOUNT_TOOLTIP = "Eliminar Conta"
    OPEN_POSTINGS = "Abrir Lançamentos"
    OPEN_MONTHLY_VIEW = "Abrir Visão Mensal"
    ERROR_OPENING_WINDOW = "Abertura automática de janela de lançamentos da conta: {0} não foi possível.\nConta não encontrada!"


class ContasView(QWidget):
    class Column(IntEnum):
        ID = 0
        DESCRICAO = auto()
        NUMERO = auto()
        MOEDA = auto()
        TIPO = auto()
        TOTAL = auto()
        N_CLASSIF = auto()
        CLASSIFIC = auto()
        REMOVER = auto()
        LANCAMENTOS = auto()
        VISAO_MENSAL = auto()

    COLUMNS = {
        Column.ID: {"title": "ID", "sql_colname": "_id"},
        Column.DESCRICAO: {"title": "Descrição", "sql_colname": "descricao"},
        Column.NUMERO: {"title": "Número", "sql_colname": "numero"},
        Column.MOEDA: {"title": "Moeda", "sql_colname": "moeda"},
        Column.TIPO: {"title": "Tipo", "sql_colname": "tipo_id"},
        Column.TOTAL: {"title": "Total"},
        Column.N_CLASSIF: {"title": "Ñ classif."},
        Column.CLASSIFIC: {"title": "Classif."},
        Column.REMOVER: {"title": "Remover"},
        Column.LANCAMENTOS: {"title": "Lanç."},
        Column.VISAO_MENSAL: {"title": "Vis. Mensal"},
    }

    def __init__(self, parent: QMainWindow):
        super(ContasView, self).__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        components = ContasViewComponents(self)
        self.main_window = parent
        self.toolbar = CustomToolbar()
        self.table = QTableView()
        self.model_tps_conta: ContasTipo = ContasTipo()
        self.model_contas = Contas()
        self.lanc_windows_open: Tuple[view.lanc_vw.LancamentosView] = {}
        self.visao_geral_window = None

        components.add_toolbar()
        components.add_table()

    def on_add_conta(self, show_message=True):
        logging.debug("Adding new conta in the database...")
        conta_id = self.model_contas.add_new(Conta(None, "nova conta", "", "BRL", "1", 0, 0, 0))
        logging.debug(f"Feito !!! Conta criada com id: {conta_id}")
        logging.debug("Reloading data...")
        self.load_table_data()

    def on_del_conta(self, index: QModelIndex):
        model: QStandardItemModel = index.model()
        conta_id = model.index(index.row(), self.Column.ID).data(Qt.UserRole)

        button = QMessageBox.question(
            self,
            TEXTS.REMOVE_ACCOUNT_TITLE,
            TEXTS.REMOVE_ACCOUNT_QUESTION.format(conta_id),
            buttons=QMessageBox.Yes | QMessageBox.No,
            defaultButton=QMessageBox.No,
        )
        if button == QMessageBox.No:
            return

        logging.debug(f"Eliminando conta {conta_id} do banco de dados ...")
        self.model_contas.delete(conta_id)
        logging.debug("Done !!!")
        logging.debug("Reloading data...")
        self.load_table_data()

    def on_open_lancamentos(self, index: QModelIndex):
        model: QStandardItemModel = index.model()
        conta_id = model.index(index.row(), self.Column.ID).data(Qt.UserRole)
        conta_dc = self.model_contas.find_by_id(conta_id)

        if conta_id not in self.lanc_windows_open:
            lancamentos_window = view.lanc_vw.LancamentosView(self, conta_dc)
            lancamentos_window.changed.connect(self.handle_lancamento_changed)
            lancamentos_window.add_lancamento.connect(self.handle_lancamento_created)
            lancamentos_window.on_close_signal.connect(self.handle_close_lancamento)
            lancamentos_window.on_delete.connect(self.handle_delete_lancamento)
            lancamentos_window.records_added.connect(self.load_table_data)
            self.lanc_windows_open[conta_id] = lancamentos_window
        else:
            lancamentos_window = self.lanc_windows_open[conta_id]

        if lancamentos_window.isHidden():
            position = lancamentos_window.pos()
            logging.debug(f"Abrir janela Lanç. (conta id: {conta_id}) posição (X: {position.x()}, Y: {position.y()}).")

            lancamentos_window.show()

        lancamentos_window.activateWindow()

    def on_open_visao_mensal(self, index: QModelIndex):
        model: QStandardItemModel = index.model()
        conta_id = model.index(index.row(), self.Column.ID).data(Qt.UserRole)
        conta = self.model_contas.find_by_id(conta_id)
        if not conta:
            logging.error(f"Conta {conta_id} não encontrada!")
            return

        self.visao_geral_window = VisaoGeralView(self, conta)
        self.visao_geral_window.show()

    def handle_close_lancamento(self, sender: view.lanc_vw.LancamentosView):
        del self.lanc_windows_open[sender.conta_dc.id]

    def handle_lancamento_created(self, lancamento_id: int):
        logging.info(f"Lancamento criado {lancamento_id}, recarregando dados na contas view.")
        self.load_table_data()

    def handle_lancamento_changed(self, lancamento: ORMLancamentos, field: str):
        logging.info(f"Lancamento modificado {lancamento.id}, recarregando dados na contas view.")
        if field == "categoria_id":
            self.load_table_data()

    def handle_delete_lancamento(self, lancamento_id: int):
        logging.info(f"Lancamento eliminado {lancamento_id}, recarregando dados na contas view.")
        self.load_table_data()

    def model_item_changed(self, item: QModelIndex):
        row = item.row()
        col = item.column()

        conta_dc = self.model_contas.items[row]
        value = item.data(Qt.UserRole)

        column_data = self.COLUMNS.get(col)

        logging.debug(
            f"Modificando conta numero:{conta_dc.id} campo \"{column_data['sql_colname']}\" para valor \"{value}\""
        )
        self.model_contas.update(conta_dc.id, column_data["sql_colname"], value)

    def load_table_data(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        model = self.table.model()
        try:
            logging.debug("Disconnecting model.itemChanged...")
            model.itemChanged.disconnect()
        except Exception as e:
            logging.error(f"model.itemChanged was not connected! Error: {e}")

        logging.debug("Loading contas data...")
        self.model_contas.load()

        # Limpa a tabela
        model.setRowCount(0)

        line = ContaTableLine(self)

        rows = self.model_contas.items

        logging.debug("Preenchendo dados na tabela.")
        for row in rows:
            new_index = model.rowCount()
            model.insertRow(new_index)

            model.setItemData(
                model.index(new_index, self.Column.ID),
                {Qt.DisplayRole: row.id, Qt.UserRole: row.id},
            )
            model.setItemData(
                model.index(new_index, self.Column.DESCRICAO),
                {Qt.DisplayRole: row.descricao, Qt.UserRole: row.descricao},
            )
            model.setItemData(
                model.index(new_index, self.Column.NUMERO),
                {Qt.DisplayRole: row.numero, Qt.UserRole: row.numero},
            )
            model.setItemData(
                model.index(new_index, self.Column.MOEDA),
                {Qt.DisplayRole: row.moeda, Qt.UserRole: row.moeda},
            )
            tipo_conta_descr = next(
                (item.descricao for item in self.model_tps_conta.items if item.id == row.tipo_id), ""
            )
            model.setItemData(
                model.index(new_index, self.Column.TIPO),
                {Qt.DisplayRole: tipo_conta_descr, Qt.UserRole: row.tipo_id},
            )
            model.setItemData(
                model.index(new_index, self.Column.TOTAL),
                {Qt.DisplayRole: curr.str_curr_to_locale(row.total or 0), Qt.UserRole: row.total},
            )
            model.setItemData(
                model.index(new_index, self.Column.N_CLASSIF),
                {Qt.DisplayRole: row.lanc_n_class, Qt.UserRole: row.lanc_n_class * -1},
            )
            model.setItemData(
                model.index(new_index, self.Column.CLASSIFIC),
                {Qt.DisplayRole: row.lanc_classif, Qt.UserRole: row.lanc_classif},
            )

        self.table.setItemDelegateForColumn(self.Column.ID, IDLabelDelegate(self.table))
        self.table.setItemDelegateForColumn(self.Column.DESCRICAO, GenericInputDelegate(self.table))
        self.table.setItemDelegateForColumn(self.Column.NUMERO, GenericInputDelegate(self.table))
        self.table.setItemDelegateForColumn(self.Column.MOEDA, GenericInputDelegate(self.table))
        self.table.setItemDelegateForColumn(
            self.Column.TIPO, ContaTableLine.get_tipo_conta_dropdown_delegate(self.table, self.model_tps_conta)
        )
        self.table.setItemDelegateForColumn(self.Column.TOTAL, CurrencyLabelDelegate(self.table, bold=True))
        self.table.setItemDelegateForColumn(
            self.Column.N_CLASSIF, CurrencyLabelDelegate(self.table, bold=True, center=True)
        )
        self.table.setItemDelegateForColumn(
            self.Column.CLASSIFIC, CurrencyLabelDelegate(self.table, bold=True, center=True)
        )
        self.table.setItemDelegateForColumn(
            self.Column.REMOVER, ButtonDelegate(self.table, ContaTableLine.get_del_button(), self.on_del_conta)
        )
        self.table.setItemDelegateForColumn(
            self.Column.LANCAMENTOS,
            ButtonDelegate(self.table, ContaTableLine.get_open_lanc_button(), self.on_open_lancamentos),
        )
        self.table.setItemDelegateForColumn(
            self.Column.VISAO_MENSAL,
            ButtonDelegate(self.table, ContaTableLine.get_visao_mensal(), self.on_open_visao_mensal),
        )

        self.table.setColumnWidth(self.Column.ID, 100)
        self.table.resizeColumnToContents(self.Column.DESCRICAO)
        self.table.resizeColumnToContents(self.Column.NUMERO)
        self.table.resizeColumnToContents(self.Column.MOEDA)
        self.table.setColumnWidth(self.Column.TIPO, 230)
        self.table.setColumnWidth(self.Column.TOTAL, 220)
        self.table.setColumnWidth(self.Column.N_CLASSIF, 120)
        self.table.setColumnWidth(self.Column.CLASSIFIC, 120)
        self.table.setColumnWidth(self.Column.REMOVER, 100)
        self.table.setColumnWidth(self.Column.LANCAMENTOS, 100)
        self.table.setColumnWidth(self.Column.VISAO_MENSAL, 100)

        model.itemChanged.connect(self.model_item_changed)
        logging.debug("Method itemChanged connected again!")
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

    def get_label_for_total_curr(self, value: int):
        label = super().get_label_for_currency(value)
        color = "color:darkgreen"
        if value < 0:
            color = "color:red"
        stylesheet = f"margin-right:3px; margin-left:3px; font-weight:bold;{color}"
        label.setStyleSheet(stylesheet)
        return label

    def get_number_input(self, numero: int):
        line_edit = QLineEdit()
        line_edit.setText(str(numero))
        line_edit.setValidator(QIntValidator())
        line_edit.textChanged.connect(self.check_state)
        line_edit.textChanged.emit(line_edit.text())

        return line_edit

    def check_state(self, *args, **kwargs):
        logging.debug("entered validator", args[0])
        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QValidator.Acceptable:
            color = "#c4df9b"  # green
        elif state == QValidator.Intermediate:
            color = "#fff79a"  # yellow
        else:
            color = "#f6989d"  # red
        sender.setStyleSheet("QLineEdit { background-color: %s }" % color)

    @staticmethod
    def get_tipo_conta_dropdown_delegate(table: QTableView, model_tps_conta: ContasTipo) -> ComboBoxDelegate:
        tipos_conta = {}
        for item in model_tps_conta.items:
            tipos_conta[item.id] = item.descricao

        cmb_delegate = ComboBoxDelegate(tipos_conta, table)

        return cmb_delegate

    def tipo_conta_dropdown_change(self, combobox: QComboBox, conta: Conta):
        data = combobox.currentData()
        conta.tipo_id = data
        self.parentOne.model_contas.update(conta)

    @staticmethod
    def get_del_button() -> QPushButton:
        del_pbutt = QPushButton()
        del_pbutt.setToolTip(TEXTS.REMOVE_ACCOUNT_TOOLTIP)
        del_pbutt.setIcon(icons.delete())
        return del_pbutt

    @staticmethod
    def get_open_lanc_button() -> QPushButton:
        op_lanc_pbutt = QPushButton()
        op_lanc_pbutt.setToolTip(TEXTS.OPEN_POSTINGS)
        op_lanc_pbutt.setIcon(icons.open_lancamentos())
        return op_lanc_pbutt

    @staticmethod
    def get_visao_mensal() -> QPushButton:
        op_lanc_pbutt = QPushButton()
        op_lanc_pbutt.setToolTip(TEXTS.OPEN_MONTHLY_VIEW)
        op_lanc_pbutt.setIcon(icons.visao_mensal())
        return op_lanc_pbutt


class ContasViewComponents:
    def __init__(self, parent: ContasView):
        super(ContasViewComponents, self).__init__()
        self.parent = parent

    def add_toolbar(self) -> None:
        layout = self.parent.layout()
        add_act = self.parent.toolbar.addAction(icons.add(), TEXTS.ADD_ACCOUNT_BTN_TEXT)
        add_act.triggered.connect(lambda: self.parent.on_add_conta())
        self.parent.toolbar.addSeparator()
        refresh_act = self.parent.toolbar.addAction(icons.atualizar(), TEXTS.REFRESH)
        refresh_act.triggered.connect(lambda: self.parent.load_table_data())
        layout.addWidget(self.parent.toolbar)

    def add_table(self):
        layout = self.parent.layout()
        model = QStandardItemModel(0, len(self.parent.COLUMNS))
        model.setHorizontalHeaderLabels([col["title"] for col in self.parent.COLUMNS.values()])
        self.parent.table.setModel(model)
        self.parent.table.verticalHeader().setVisible(False)
        self.parent.load_table_data()

        layout.addWidget(self.parent.table)
