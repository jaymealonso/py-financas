from enum import IntEnum, auto

from PyQt5.QtCore import QEvent, QItemSelectionModel, QModelIndex, Qt, pyqtSignal
from PyQt5.QtGui import QCursor, QKeySequence, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableView,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
from unidecode import unidecode

import util.curr_formatter as curr
from lib.Genericos.log import logging
from lib.Lancamentos.SortFilterProxy import LancamentoSortFilterProxyModel
from model.Anexos import Anexos
from model.Categoria import Categorias
from model.Conta import Conta
from model.Lancamento import Lancamentos
from model.db.db_orm import Anexos as ORMAnexos, Lancamentos as ORMLancamentos
from util.currency_editor import QCurrencyLineEdit
from util.custom_table_delegates import (
    ComboBoxDelegate,
    CurrencyEditDelegate,
    CurrencyLabelDelegate,
    DateEditDelegate,
    GenericInputDelegate,
    IDLabelDelegate,
)
from util.my_dialog import MyDialog
from util.settings import JanelaLancamentosSettings, Settings
from util.toaster import QToaster

import view.contas_vw as cv
import view.icons.icons as icons
from view.anexos_vw import AnexosView
from view.imp_lanc_vw import ImportarLancamentosView
from lib.Lancamentos.InputSearchTable import ColumnSearchView
from view.TableLine import TableLine


class LancamentosView(MyDialog):
    # lancamento: ORMLancamentos, field:str
    changed = pyqtSignal(ORMLancamentos, str)
    # lancamento_id: int
    add_lancamento = pyqtSignal(int)
    # lancamento_id: int
    on_delete = pyqtSignal(int)

    records_added = pyqtSignal()

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
        Column.ID: {"title": "ID", "sql_colname": "id", "col_width": 90 },
        Column.SEQ_ORDEM_LINHA: { "title": "Seq Linha", "sql_colname": "seq_ordem_linha", "col_width": 100 },
        Column.NR_REFERENCIA: { "title": "Número Ref.", "sql_colname": "nr_referencia", "col_width": 100 },
        Column.DESCRICAO: {"title": "Descrição", "sql_colname": "descricao", "col_width": 500},
        Column.DESCRICAO_USER: {"title": "Descrição Usuário", "sql_colname": "descricao_user", "col_width": 100},
        Column.DATA: {"title": "Data", "sql_colname": "data", "col_width": 160},
        Column.CATEGORIA_ID: {"title": "Categorias", "sql_colname": "categoria_id", "col_width": 260},
        Column.VALOR: {"title": "Valor", "sql_colname": "valor", "col_width": 160},
        Column.SALDO: {"title": "Saldo", "col_width": 160},
        Column.REMOVER: {"title": "Remover", "col_width": 100},
        Column.ANEXOS: {"title": "Anexos", "col_width": 100},
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

        rem_act = toolbar.addAction(icons.delete(), "Eliminar selecionados")
        rem_act.triggered.connect(lambda: self.on_rem_lancamentos())

        return toolbar

    def get_table(self) -> QTableView:
        """
        Retorna tabela com o seu layout
        """
        self.table = QTableView()

        model = QStandardItemModel(0, len(self.COLUMNS))
        model.setHorizontalHeaderLabels([col["title"] for col in self.COLUMNS.values()])

        sortModel = LancamentoSortFilterProxyModel(self)
        sortModel.setSourceModel(model)
        self.table.setModel(sortModel)
        self.table.setSortingEnabled(True)

        self.table.verticalHeader().setVisible(False)
        # Enable context menu on the column header
        hheader = self.table.horizontalHeader()
        hheader.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.horizontalHeader().customContextMenuRequested.connect(self.on_table_header_context_menu)

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
        self.import_lanc_view.importacao_finalizada.connect(self.on_import_finalizada)
        self.import_lanc_view.show()

    def on_import_finalizada(self):
        self.load_model_only()
        self.records_added.emit()

    def open_search(self, logical_index):
        col = self.COLUMNS.get(logical_index)
        if not self.search_dialog:
            self.search_dialog = ColumnSearchView(self)
            self.layout().insertWidget(1, self.search_dialog)
        self.search_dialog.show2(col["title"], logical_index)
        self.search_dialog.on_close_signal.connect(self.on_close_search_dialog)

    def on_close_search_dialog(self):
        self.search_dialog = None

    def on_table_header_context_menu(self, point):
        hheader = self.table.horizontalHeader()
        column = self.table.indexAt(point)
        column_id = column.column()
        if column_id < 2 or column_id > 8:
            return

        menu = QMenu(self)
        menu.addAction( QAction(icons.tab_search(), 'Procurar', menu, 
            shortcut=QKeySequence("Ctrl+f") , 
            triggered=lambda: self.open_search(column_id)))
        menu.popup(hheader.mapToGlobal(point))

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

    def on_rem_lancamentos(self):
        item: QModelIndex = None
        list_of_indx = []
        for item in self.table.selectedIndexes():
            lanc_id = item.model().index(item.row(), 0).data(Qt.UserRole)
            list_of_indx.append({"index": item.row(), "id": str(lanc_id)})

        selected_count = len(list_of_indx)

        if selected_count == 0:
            QMessageBox.critical(self, "Erro", "Selecionar ao menos uma linha.")
            return

        pop_answer = QMessageBox.question(
            self,
            "Remove Lancamentos?",
            f"Deseja remover { selected_count } lançamentos ?",
            buttons=QMessageBox.Yes | QMessageBox.No,
            defaultButton=QMessageBox.No,
        )
        if pop_answer == QMessageBox.No:
            return

        logging.debug(f"Inicia a eliminação de {selected_count} registros.")
        for item in list_of_indx:
            self.model_lancamentos.delete(item["id"])

            self.table.model().removeRow(item["index"])
            self.load_model_only()

        logging.debug("Finalizada a eliminação !!!")
        self.on_delete.emit(-1)

    def load_model_only(self, rerender_buttons: bool = True):
        self.model_lancamentos.load()

        filter_model:LancamentoSortFilterProxyModel = self.table.model()
        model:QStandardItemModel = filter_model.sourceModel()
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
                {Qt.DisplayRole: row.descricao, Qt.UserRole: row.descricao, Qt.AccessibleTextRole: unidecode(row.descricao)},
            )
            model.setItemData(
                model.index(new_index, self.Column.DESCRICAO_USER),
                {Qt.DisplayRole: row.descricao_user, Qt.UserRole: row.descricao_user, Qt.AccessibleTextRole: unidecode(row.descricao_user)},
            )
            model.setItemData(
                model.index(new_index, self.Column.DATA),
                {Qt.DisplayRole: row.data.strftime("%x"), Qt.UserRole: row.data, Qt.AccessibleTextRole: row.data},
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
                    Qt.AccessibleTextRole: unidecode(categoria.nm_categoria)
                },
            )
            model.setItemData(
                model.index(new_index, self.Column.VALOR),
                {
                    Qt.DisplayRole: curr.str_curr_to_locale(row.valor or 0),
                    Qt.UserRole: row.valor or 0,
                    Qt.AccessibleTextRole: row.valor or 0,
                },
            )
            saldo += row.valor
            model.setItemData(
                model.index(new_index, self.Column.SALDO),
                {
                    Qt.DisplayRole: curr.str_curr_to_locale(saldo or 0),
                    Qt.UserRole: saldo,
                    Qt.AccessibleTextRole: saldo,
                },
            )
            if rerender_buttons:
                self.table.setIndexWidget(
                    filter_model.index(new_index, self.Column.REMOVER),
                    # model.index(new_index, self.Column.REMOVER),
                    self.tableline.get_del_button(self, row.id),
                )

                self.table.setIndexWidget(
                    filter_model.index(new_index, self.Column.ANEXOS),
                    # model.index(new_index, self.Column.ANEXOS),
                    self.tableline.get_attach_button(self, row.nr_anexos, row.id),
                )

        filter_model.setSourceModel(model)
        self.table.setModel(filter_model)

        # Define valor do TOTAL que aparece no rodapé da janela
        self.total_label.set_int_value(self.model_lancamentos.total)

    def load_table_data(self):
        """ Popula tabela com os dados do modelo, redimensiona colunas """
        # reset sort order
        self.table.sortByColumn(-1, Qt.AscendingOrder)

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
        self.table.setItemDelegateForColumn(self.Column.SALDO, CurrencyLabelDelegate(self.table, bold=True))

        logging.debug("> itemChanged connected again!")
        self.table.verticalScrollBar().setValue(vert_scr_position)
        QApplication.restoreOverrideCursor()

    def on_model_item_changed(self, item: QStandardItem):
        """
        Disparado pela modificação de um WIDGET na linha da tabela
        """
        self.table_cell_changed(item)

    def set_column_default_sizes(self):        
        for index, col in self.COLUMNS.items():
            self.table.setColumnWidth(index, col.get("col_width"))

    def set_filter_mes_categ(self, filters: dict[str, str]):
        filter_model: LancamentoSortFilterProxyModel = self.table.model()

        filter_model.clear_filters()
        if len(filters) == 0:
            self.show_all()
        for mes_ano, categoria in filters:
            filter_model.add_filter(mes_ano, categoria)
        filter_model.invalidateFilter()

    def show_all(self):
        filter_model: LancamentoSortFilterProxyModel = self.table.model()
       
        filter_model.setFilterRegExp(".*")

    def keyPressEvent(self, e:QEvent) -> None:
        """Evento Ctrl + F para chamar a busca na coluna"""
        if e.key() == (Qt.Key_Control and Qt.Key_F):
            index = next((sel_ind for sel_ind in self.table.selectedIndexes()), None)
            if not index:
                return

            if index.column() not in (
                self.Column.ID,
                self.Column.SEQ_ORDEM_LINHA,
                self.Column.NR_REFERENCIA,
                self.Column.DESCRICAO,
                self.Column.DESCRICAO_USER,
                self.Column.DATA, 
                self.Column.CATEGORIA_ID, 
                self.Column.VALOR, 
                self.Column.SALDO, 
            ):
                return

            self.open_search(index.column())
            logging.debug(e)
            return
        
        return super(LancamentosView, self).keyPressEvent(e)



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
        super(LancamentoTableLine, self).__init__()
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

    def get_currency_input(self, valor: int, row: int, col: int) -> QCurrencyLineEdit:
        line_edit = QCurrencyLineEdit(self)
        line_edit.setTextInt(valor)
        return line_edit

    def on_curr_input_text_changed(self, *args, **kwargs) -> None:
        self.sender().setTextFormat()

    def get_label_for_saldo(self, value: int) -> QLineEdit:
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
