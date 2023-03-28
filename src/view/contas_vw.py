import view.icons.icons as icons
import view.lanc_vw
import logging
from view.TableLine import TableLine
from view.visao_mensal_vw import VisaoGeralView
from typing import Tuple
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import (
    QIntValidator,
    QValidator,
    QCursor,
    QStandardItemModel,
    QColor,
)
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QToolBar,
    QComboBox,
    QLineEdit,
    QPushButton,
    QMainWindow,
    QMessageBox,
    QApplication,
    QTableView,
    QTableWidgetItem,
)
from model.Conta import ContasTipo, Contas, Conta
from util.events import subscribe, unsubscribe_refs, Eventos
from util.custom_table_delegates import GenericInputDelegate, ComboBoxDelegate

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


class ContasView(QWidget):
    COLUMNS = {
        0: {"title": "ID", "sql_colname": "_id"},
        1: {"title": "Descrição", "sql_colname": "descricao"},
        2: {"title": "Número", "sql_colname": "numero"},
        3: {"title": "Moeda", "sql_colname": "moeda"},
        4: {"title": "Tipo", "sql_colname": "tipo_id"},
        5: {"title": "Total"},
        6: {"title": "Ñ classif."},
        7: {"title": "Classif."},
        8: {"title": "Remover"},
        9: {"title": "Lanç."},
        10: {"title": "Vis. Mensal"},
    }

    def __init__(self, parent: QMainWindow):
        super(ContasView, self).__init__()

        layout = QVBoxLayout()

        self.main_window = parent
        self.toolbar = QToolBar()
        self.table = QTableView()
        self.model_tps_conta: ContasTipo = ContasTipo()
        self.model_contas = Contas()
        self.lanc_windows_open: Tuple[view.lanc_vw.LancamentosView] = {}
        self.visao_geral_window = None

        layout.addWidget(self.get_toolbar())
        layout.addWidget(self.get_table())

        self.setLayout(layout)

    def get_toolbar(self):
        add_act = self.toolbar.addAction(icons.add(), "Adicionar Conta")
        add_act.triggered.connect(lambda: self.on_add_conta())
        self.toolbar.addSeparator()
        refresh_act = self.toolbar.addAction(icons.atualizar(), "Atualizar")
        refresh_act.triggered.connect(lambda: self.load_table_data())

        return self.toolbar

    def on_add_conta(self, show_message=True):
        logging.debug("Adding new conta in the database...")
        self.model_contas.add_new(Conta(None, "nova conta", "", "BRL", "1", 0, 0, 0))
        logging.debug("Done !!!")
        logging.debug("Reloading data...")
        self.load_table_data()

    def on_del_conta(self, conta_id: int):
        button = QMessageBox.question(
            self,
            "Remove conta?",
            f"Deseja remover a conta {conta_id} ?",
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

    def on_open_lancamentos(self, conta_id: int):
        conta_dc = self.model_contas.find_by_id(conta_id)
        if not conta_dc:
            QMessageBox(
                text=f"Abertura automática de janela de lançamentos da conta: {conta_id} não foi possível.\nConta não encontrada!"
            ).exec()
            return
        
        if conta_id not in self.lanc_windows_open:
            lancamentos_window = view.lanc_vw.LancamentosView(self, conta_dc)
            subscribe(
                Eventos.LANCAMENTO_CREATED,
                self.handle_lancamento_created,
                lancamentos_window,
            )
            subscribe(
                Eventos.LANCAMENTO_WINDOW_CLOSED,
                self.handle_close_lancamento,
                lancamentos_window,
            )
            self.lanc_windows_open[conta_id] = lancamentos_window
        else:
            lancamentos_window = self.lanc_windows_open[conta_id]

        if lancamentos_window.isHidden():
            position = self.main_window.pos()
            logging.debug(
                f"Abrir janela Lanç. (conta id:{conta_id}) posição (X: {position.x()}, Y: {position.y()})."
            )

            lancamentos_window.show()

        lancamentos_window.activateWindow()

    def on_open_visao_mensal(self, conta_id: int):
        conta = self.model_contas.find_by_id(conta_id)
        if not conta:
            logging.error(f"Conta {conta_id} não encontrada!")
            return
        
        self.visao_geral_window = VisaoGeralView(self, conta)
        self.visao_geral_window.show()

    def handle_close_lancamento(self, conta_id: int):
        logging.debug(f"Lancamento close event UNSUBSCRIBE conta: {conta_id}")
        unsubscribe_refs(self.lanc_windows_open[conta_id])
        del self.lanc_windows_open[conta_id]

    def handle_lancamento_created(self, lancamento_id: int):
        logging.debug(
            f"Lancamento criado {lancamento_id}, recarregando dados na contas view."
        )
        self.load_table_data()

    def get_table(self):
        model = QStandardItemModel(0, len(self.COLUMNS))
        model.setHorizontalHeaderLabels([col["title"] for col in self.COLUMNS.values()])
        self.table.setModel(model)
        self.table.verticalHeader().setVisible(False)
        self.load_table_data()

        return self.table

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
            logging.error("model.itemChanged was not connected! Error: {e}")

        logging.debug("Loading contas data...")
        self.model_contas.load()

        # Limpa a tabela
        model.setRowCount(0)

        line = ContaTableLine(self)

        self.table.setItemDelegateForColumn(4, line.get_tipo_conta_dropdown_delegate())

        rows = self.model_contas.items

        logging.debug("Preenchendo dados na tabela.")
        for row in rows:
            new_index = model.rowCount()
            model.insertRow(new_index)

            self.table.setIndexWidget(
                model.index(new_index, 0), line.get_label_for_id(str(row.id))
            )

            model.setItemData(
                model.index(new_index, 1),
                {Qt.DisplayRole: row.descricao, Qt.UserRole: row.descricao},
            )
            model.setItemData(
                model.index(new_index, 2),
                {Qt.DisplayRole: row.numero, Qt.UserRole: row.numero},
            )
            model.setItemData(
                model.index(new_index, 3),
                {Qt.DisplayRole: row.moeda, Qt.UserRole: row.moeda},
            )
            model.setItemData(
                model.index(new_index, 4),
                {Qt.DisplayRole: row.tipo_id, Qt.UserRole: row.tipo_id},
            )

            # Fixed Values
            self.table.setIndexWidget(
                model.index(new_index, 5), line.get_label_for_total_curr(row.total)
            )
            self.table.setIndexWidget(
                model.index(new_index, 6), line.get_label_for_n_class(row.lanc_n_class)
            )
            self.table.setIndexWidget(
                model.index(new_index, 7), line.get_label_for_classif(row.lanc_classif)
            )

            # Buttons
            self.table.setIndexWidget(
                model.index(new_index, 8), line.get_del_button(row.id)
            )
            self.table.setIndexWidget(
                model.index(new_index, 9), line.get_open_lanc_button(row.id)
            )
            self.table.setIndexWidget(
                model.index(new_index, 10), line.get_visao_mensal(row.id)
            )

        self.table.setItemDelegateForColumn(1, GenericInputDelegate(self.table))
        self.table.setItemDelegateForColumn(2, GenericInputDelegate(self.table))
        self.table.setItemDelegateForColumn(3, GenericInputDelegate(self.table))

        self.table.setColumnWidth(0, 100)
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

    def get_tipo_conta_dropdown_delegate(self):
        tipos_conta = {}
        for item in self.parentOne.model_tps_conta.items:
            tipos_conta[item.id] = item.descricao

        cmb_delegate = ComboBoxDelegate(tipos_conta, self.parentOne.table)

        return cmb_delegate

    def get_tipo_conta_dropdown(self, conta: Conta):
        combobox = QComboBox()
        index: int = 0
        items = self.parentOne.model_tps_conta.items
        for key, item_index in enumerate(items):
            item = items.get(item_index)
            if item.id == conta.tipo_id:
                index = key
            combobox.addItem(item.descricao, item.id)

        combobox.setCurrentIndex(index)
        combobox.currentIndexChanged.connect(
            lambda: self.tipo_conta_dropdown_change(combobox, conta)
        )
        return combobox

    def tipo_conta_dropdown_change(self, combobox: QComboBox, conta: Conta):
        data = combobox.currentData()
        conta.tipo_id = data
        self.parentOne.model_contas.update(conta)

    def get_del_button(self, conta_id: int):
        del_pbutt = QPushButton()
        del_pbutt.setToolTip("Eliminar Conta")
        del_pbutt.setIcon(icons.delete())
        del_pbutt.clicked.connect(lambda: self.parentOne.on_del_conta(conta_id))
        return del_pbutt

    def get_open_lanc_button(self, conta_id: int):
        op_lanc_pbutt = QPushButton()
        op_lanc_pbutt.setToolTip("Abrir Lançamentos")
        op_lanc_pbutt.setIcon(icons.open_lancamentos())
        op_lanc_pbutt.clicked.connect(
            lambda: self.parentOne.on_open_lancamentos(conta_id)
        )
        return op_lanc_pbutt

    def get_visao_mensal(self, conta_id: int):
        op_lanc_pbutt = QPushButton()
        op_lanc_pbutt.setToolTip("Abrir Visão Mensal")
        op_lanc_pbutt.setIcon(icons.visao_mensal())
        op_lanc_pbutt.clicked.connect(
            lambda: self.parentOne.on_open_visao_mensal(conta_id)
        )
        return op_lanc_pbutt
