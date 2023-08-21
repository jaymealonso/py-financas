from model.Anexos import Anexos
import view.icons.icons as icons
import view.contas_vw as cv
import logging

from util.my_dialog import MyDialog
from view.imp_lanc_vw import ImportarLancamentosView
from view.anexos_vw import AnexosView
from view.TableLine import TableLine
from model.Conta import Conta
from model.Categoria import Categorias
from model.Lancamento import Lancamentos
from model.db.db_orm import (
    Lancamentos as ORMLancamentos,
    Anexos as ORMAnexos,
)
from PyQt5.QtGui import (
    QStandardItemModel,
    QCursor,
    QStandardItem,
)
from PyQt5.QtCore import Qt, QObject, QModelIndex, pyqtSignal, QItemSelectionModel
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QTableView,
    QPushButton,
    QToolBar,
    QSizePolicy,
    QMessageBox,
    QLabel,
    QCheckBox,
    QApplication,
    QDialog,
)
from util.toaster import QToaster
from util.currency_editor import QCurrencyLineEdit
import util.curr_formatter as curr
from util.settings import Settings, JanelaLancamentosSettings
from util.custom_table_delegates import (
    GenericInputDelegate,
    ComboBoxDelegate,
    DateEditDelegate,
    CurrencyEditDelegate, CurrencyLabelDelegate, IDLabelDelegate,
)
from enum import auto, IntEnum

from view.inputsearch_vw import ColumnSearchView

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


class LancamentosView(MyDialog):
    # lancamento: ORMLancamentos, field:str
    changed = pyqtSignal(ORMLancamentos, str)
    # lancamento_id: int
    add_lancamento = pyqtSignal(int)
    # lancamento_id: int
    on_delete = pyqtSignal(int)

    class Column(IntEnum):
        ID = 0
        SEQ_ORDEM_LINHA = auto()
        NR_REFERENCIA = auto()
        DESCRICAO = auto()
        DESCRICAO_USER = auto()
        DATA = auto()
        CATEGORIA_ID = auto()
        VALOR = auto()
        SALDO = auto()
        REMOVER = auto()
        ANEXOS = auto()

    COLUMNS = {
        Column.ID: {"title": "ID", "sql_colname": "id"},
        Column.SEQ_ORDEM_LINHA: {
            "title": "Seq Linha",
            "sql_colname": "seq_ordem_linha",
        },
        Column.NR_REFERENCIA: {
            "title": "Número Ref.",
            "sql_colname": "nr_referencia",
        },
        Column.DESCRICAO: {"title": "Descrição", "sql_colname": "descricao"},
        Column.DESCRICAO_USER: {"title": "Descrição Usuário", "sql_colname": "descricao_user"},
        Column.DATA: {"title": "Data", "sql_colname": "data"},
        Column.CATEGORIA_ID: {"title": "Categorias", "sql_colname": "categoria_id"},
        Column.VALOR: {"title": "Valor", "sql_colname": "valor"},
        Column.SALDO: {"title": "Saldo"},
        Column.REMOVER: {"title": "Remover"},
        Column.ANEXOS: {"title": "Anexos"},
    }

    def __init__(self, parent: QWidget, conta_dc: Conta):

        super(LancamentosView, self).__init__(parent)

        self.toolbar = self.get_toolbar()
        table: QTableView = self.get_table()
        self.tableline = LancamentoTableLine(self)
        self.conta_dc = conta_dc
        self.parent: cv.ContasView = parent
        self.import_lanc_view = None
        self.search_dialog = None
        self.total_label = TotalCurrLabel()
        self.model_lancamentos = Lancamentos(conta_dc)
        self.model_categorias = Categorias()
        self.model_categorias.load()
        self.global_settings = Settings()
        self.settings: JanelaLancamentosSettings = (
            self.global_settings.load_lanc_settings(self.conta_dc.id)
        )
        self.setWindowTitle(
            f"Lançamentos - (Conta {self.conta_dc.id} | {self.conta_dc.descricao})"
        )
        self.restore_geometry()
        self.on_close_signal.connect(self.on_close)

        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(table)
        layout.addWidget(self.get_footer())

        self.setLayout(layout)

        self.load_table_data()
        self.set_column_default_sizes()

    def on_close(self):
        self.settings.dimensoes = self.saveGeometry()

    def restore_geometry(self) -> None:
        self.setMinimumSize(800, 600)
        try:
            self.restoreGeometry(self.settings.dimensoes)
        except Exception as e:
            logging.error(str(e))
            self.resize(1600, 900)

    def get_toolbar(self) -> QToolBar:
        """
        Retorna toolbar
        """
        toolbar: QToolBar = QToolBar()
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        import_act = toolbar.addAction(icons.import_file(), "Importar Lançamentos")
        import_act.triggered.connect(self.on_import_lancam)

        refresh_act = toolbar.addAction(icons.atualizar(), "Atualizar")
        refresh_act.triggered.connect(lambda: self.load_table_data())

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer)

        self.check_del_not_ask = QCheckBox("Eliminar sem perguntar")
        toolbar.addWidget(self.check_del_not_ask)

        add_act = toolbar.addAction(icons.add(), "Novo Lançamento")
        add_act.triggered.connect(lambda: self.on_add_lancamento())

        return toolbar

    def get_table(self) -> QTableView:
        """
        Retorna tabela com o seu layout
        """
        self.table = QTableView()
        model = QStandardItemModel(0, len(self.COLUMNS))
        model.setHorizontalHeaderLabels([col["title"] for col in self.COLUMNS.values()])
        self.table.setModel(model)
        self.table.verticalHeader().setVisible(False)
        hheader = self.table.horizontalHeader()
        hheader.sectionClicked.connect(self.on_table_header_click)

        return self.table

    def get_footer(self):
        """
        Retorna rodapé com total dos lancamentos
        """
        layout = QHBoxLayout()

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout.insertStretch(0)
        layout.addWidget(QLabel("TOTAL"))
        layout.addWidget(self.total_label)

        footer = QWidget(self)
        footer.setLayout(layout)
        return footer

    def on_open_attachments(self, lancamento_id: int):
        """
        Exibe a janela de anexos
        """
        lancamento = self.model_lancamentos.get_lancamento(lancamento_id)
        if not lancamento:
            QMessageBox(text="Lanc não encontrado.").exec()
            return
        self.anexos_vw = AnexosView(self, lancamento)

        self.anexos_vw.changed.connect(self.on_changed_anexos)

        self.anexos_vw.show()

    def on_changed_anexos(self, anexo: ORMAnexos, total_anexos: int):
        self.model_lancamentos.load()
        self.load_table_data()

    def on_import_lancam(self):
        """
        Exibe a janela de importação de lançamentos
        """
        self.import_lanc_view = ImportarLancamentosView(self, self.conta_dc)
        self.import_lanc_view.show()

    def on_table_header_click(self, logical_index):
        col = self.COLUMNS.get(logical_index)
        if not self.search_dialog:
            self.search_dialog = ColumnSearchView(self)
            self.layout().insertWidget(1, self.search_dialog)
        self.search_dialog.show2(col["title"], logical_index)
        self.search_dialog.on_close_signal.connect(self.on_close_search_dialog)

    def on_close_search_dialog(self):
        self.search_dialog = None

    def table_cell_changed(self, item: QModelIndex):
        row = item.row()
        col = item.column()

        logging.debug(f"Cell changed row/col: {row}/{col}")

        model = self.table.model()
        lancamento_id = model.data(model.index(row, self.Column.ID), Qt.UserRole)
        value = model.data(item, Qt.UserRole)

        column_data = self.COLUMNS.get(col)
        sql_colname = column_data["sql_colname"]

        logging.debug(f"Modificando lancamento numero:{lancamento_id}")
        logging.debug(f'"{sql_colname}" >> "{value}"')

        # se for modificação de data, move os anexos para o novo diretório, se necessário.
        if sql_colname == "data":
            lancamento: ORMLancamentos = self.model_lancamentos.get_lancamento(
                lancamento_id
            )
            anexos = Anexos(lancamento.id)
            anexos.load()
            anexos.move_anexos(lancamento, value)

        self.model_lancamentos.update(lancamento_id, sql_colname, value)

        # recalcula total
        self.load_model_only(sql_colname == 'data')
        if sql_colname == 'data':
            item_new_indexes = model.match(model.index(0, self.Column.ID), Qt.UserRole, lancamento_id, 1)
            if len(item_new_indexes) > 0:
                item_new_index = model.index(item_new_indexes[0].row(), self.Column.DATA)
                self.table.scrollTo(item_new_index)
                self.table.selectionModel().select(item_new_index, QItemSelectionModel.SelectCurrent)
                self.table.setCurrentIndex(item_new_index)

        lancamento: ORMLancamentos = self.model_lancamentos.get_lancamento(
            lancamento_id
        )
        self.changed.emit(lancamento, sql_colname)
        self.table.setFocus()

    def on_del_lancamento(self, lancamento_id: int):

        model = self.table.model()

        items_found = model.match(model.index(0, 0), Qt.UserRole, lancamento_id, 1)
        if len(items_found) == 0:
            return
        table_row_index = items_found[0].row()

        if not self.check_del_not_ask.isChecked():
            button = QMessageBox.question(
                self,
                "Remove Lancamento?",
                f"Deseja remover o lançamento {lancamento_id} ?",
                buttons=QMessageBox.Yes | QMessageBox.No,
                defaultButton=QMessageBox.No,
            )
            if button == QMessageBox.No:
                return

        logging.debug(f"Eliminando lancamento {lancamento_id} do banco de dados ...")
        self.model_lancamentos.delete(str(lancamento_id))

        model.removeRow(table_row_index)
        self.load_model_only()

        logging.debug("Done !!!")
        self.on_delete.emit(lancamento_id)

    def on_add_lancamento(self, show_message=True):
        logging.debug("Adding new lancamento in the database...")
        new_lancamento_id = self.model_lancamentos.add_new_empty(self.conta_dc.id)

        logging.debug(f"Done !!! Lancamento criado com id: {new_lancamento_id}")
        self.add_lancamento.emit(new_lancamento_id)
        self.load_model_only()
        model = self.table.model()
        items_found = model.match(model.index(0, 0), Qt.UserRole, new_lancamento_id, 1)
        self.table.scrollTo(items_found[0])
        self.table.selectRow(items_found[0].row())

        if show_message:
            QToaster.showMessage(self, "Novo lançamento adicionado.")

    def load_model_only(self, rerender_buttons: bool = True):
        self.model_lancamentos.load()

        model = self.table.model()
        model.setRowCount(len(self.model_lancamentos.items))
        saldo = 0
        for (new_index, row) in enumerate(self.model_lancamentos.items):
            model.setItemData(
                model.index(new_index, self.Column.ID),
                {Qt.UserRole: row.id},
            )
            model.setItemData(
                model.index(new_index, self.Column.SEQ_ORDEM_LINHA),
                {Qt.UserRole: row.seq_ordem_linha},
            )
            model.setItemData(
                model.index(new_index, self.Column.NR_REFERENCIA),
                {Qt.DisplayRole: row.nr_referencia, Qt.UserRole: row.nr_referencia},
            )
            model.setItemData(
                model.index(new_index, self.Column.DESCRICAO),
                {Qt.DisplayRole: row.descricao, Qt.UserRole: row.descricao},
            )
            model.setItemData(
                model.index(new_index, self.Column.DESCRICAO_USER),
                {Qt.DisplayRole: row.descricao_user, Qt.UserRole: row.descricao_user},
            )
            model.setItemData(
                model.index(new_index, self.Column.DATA),
                {Qt.DisplayRole: row.data.strftime("%x"), Qt.UserRole: row.data},
            )
            if len(row.Categorias) > 0:
                categoria = row.Categorias[0]
            else:
                categoria = self.model_categorias.items[0]
            model.setItemData(
                model.index(new_index, self.Column.CATEGORIA_ID),
                {
                    Qt.DisplayRole: categoria.nm_categoria,
                    Qt.UserRole: categoria.id or -1,
                },
            )
            model.setItemData(
                model.index(new_index, self.Column.VALOR),
                {
                    Qt.DisplayRole: curr.str_curr_to_locale(row.valor or 0),
                    Qt.UserRole: row.valor or 0,
                },
            )
            saldo += row.valor
            model.setItemData(
                model.index(new_index, self.Column.SALDO),
                {
                    Qt.DisplayRole: curr.str_curr_to_locale(saldo or 0),
                    Qt.UserRole: saldo,
                },
            )
            if rerender_buttons:
                self.table.setIndexWidget(
                    model.index(new_index, self.Column.REMOVER),
                    self.tableline.get_del_button(self, row.id),
                )

                self.table.setIndexWidget(
                    model.index(new_index, self.Column.ANEXOS),
                    self.tableline.get_attach_button(self, row.nr_anexos, row.id),
                )

        self.table.setModel(model)
        # Define valor do TOTAL que aparece no rodapé da janela
        self.total_label.set_int_value(self.model_lancamentos.total)

    def load_table_data(self):
        """
        Popula tabela com os dados do modelo, redimensiona colunas
        """
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        vert_scr_position = self.table.verticalScrollBar().value()
        model = self.table.model()
        try:
            logging.debug("> Disconnecting table itemChanged... ")
            model.itemChanged.disconnect()
            logging.debug("Disconnected!")
        except Exception as e:
            logging.error(f"itemChanged not connected! Error: {str(e)}")

        logging.info(f"Loading lancamentos (conta id: {self.conta_dc.id}) data...")

        self.load_model_only()

        col1_del = GenericInputDelegate(self.table)
        col1_del.changed.connect(self.on_model_item_changed)
        col2_del = GenericInputDelegate(self.table)
        col2_del.changed.connect(self.on_model_item_changed)
        col3_del = self.tableline.get_date_input()
        col3_del.changed.connect(self.on_model_item_changed)
        col4_del = self.tableline.get_categoria_dropdown_delegate()
        col4_del.changed.connect(self.on_model_item_changed)
        col5_del = self.tableline.get_currency_value_delegate()
        col5_del.changed.connect(self.on_model_item_changed)
        col6_del = GenericInputDelegate(self.table)
        col6_del.changed.connect(self.on_model_item_changed)

        self.table.setItemDelegateForColumn(self.Column.ID, IDLabelDelegate(self.table))
        self.table.setItemDelegateForColumn(self.Column.SEQ_ORDEM_LINHA, IDLabelDelegate(self.table))
        self.table.setItemDelegateForColumn(self.Column.NR_REFERENCIA, col1_del)
        self.table.setItemDelegateForColumn(self.Column.DESCRICAO, col2_del)
        self.table.setItemDelegateForColumn(self.Column.DESCRICAO_USER, col6_del)
        self.table.setItemDelegateForColumn(self.Column.DATA, col3_del)
        self.table.setItemDelegateForColumn(self.Column.CATEGORIA_ID, col4_del)
        self.table.setItemDelegateForColumn(self.Column.VALOR, col5_del)
        self.table.setItemDelegateForColumn(self.Column.SALDO, CurrencyLabelDelegate(self.table))
        # self.table.setItemDelegateForColumn(self.Column.REMOVER, col8_del)
        # self.table.setItemDelegateForColumn(self.Column.ANEXOS, col7_del)

        logging.debug("> itemChanged connected again!")
        self.table.verticalScrollBar().setValue(vert_scr_position)
        QApplication.restoreOverrideCursor()

    def on_model_item_changed(self, item: QStandardItem):
        """
        Disparado pela modificação de um WIDGET na linha da tabela
        """
        self.table_cell_changed(item)

    def set_column_default_sizes(self):
        self.table.setColumnWidth(self.Column.ID, 90)
        self.table.setColumnWidth(self.Column.SEQ_ORDEM_LINHA, 100)
        self.table.setColumnWidth(self.Column.NR_REFERENCIA, 100)
        self.table.setColumnWidth(self.Column.DESCRICAO, 500)
        self.table.setColumnWidth(self.Column.DATA, 160)
        self.table.setColumnWidth(self.Column.CATEGORIA_ID, 260)
        self.table.setColumnWidth(self.Column.VALOR, 160)
        self.table.setColumnWidth(self.Column.SALDO, 160)
        self.table.setColumnWidth(self.Column.REMOVER, 100)
        self.table.setColumnWidth(self.Column.ANEXOS, 100)


class TotalCurrLabel(QLabel):
    def set_int_value(self, value_int: int):
        self.setText(curr.int_to_locale(value_int))
        color = "color:darkgreen"
        if value_int < 0:
            color = "color:red"
        stylesheet = f"margin-right:3px; margin-left:3px; font-weight:bold; {color}"
        self.setStyleSheet(stylesheet)
        self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)


class LancamentoTableLine(TableLine):
    def __init__(self, parent: LancamentosView):
        super(QObject, self).__init__()
        self.parentOne: LancamentosView = parent

    def get_currency_value_delegate(self) -> CurrencyEditDelegate:
        return CurrencyEditDelegate(self.parentOne.table)

    def get_categoria_dropdown_delegate(self):
        categorias = {}
        for item in self.parentOne.model_categorias.items:
            categorias[item.id] = item.nm_categoria

        cmb_delegate = ComboBoxDelegate(categorias, self.parentOne.table)

        return cmb_delegate

    def get_date_input(self):
        date = DateEditDelegate(self.parentOne.table)
        return date

    def get_currency_input(self, valor: int, row: int, col: int):
        line_edit = QCurrencyLineEdit()
        line_edit.setTextInt(valor)
        return line_edit

    def on_curr_input_text_changed(self, *args, **kwargs):
        self.sender().setTextFormat()

    def get_label_for_saldo(self, value: int):
        label = super().get_label_for_currency(value)
        return label

    @staticmethod
    def get_del_button(parent: LancamentosView, lancamento_id: int):
        del_pbutt = QPushButton()
        del_pbutt.setToolTip("Eliminar Lançamento")
        del_pbutt.setIcon(icons.delete())
        del_pbutt.clicked.connect(lambda: parent.on_del_lancamento(lancamento_id))
        return del_pbutt

    @staticmethod
    def get_attach_button(parent: LancamentosView, count: int, row_id: int):
        del_pbutt = QPushButton()
        del_pbutt.setToolTip("Anexos")
        del_pbutt.setIcon(icons.attach())
        text = ""
        if count > 0:
            text = str(count)
        del_pbutt.setText(text)
        del_pbutt.clicked.connect(lambda: parent.on_open_attachments(row_id))
        return del_pbutt
