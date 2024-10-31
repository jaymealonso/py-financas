import csv
from enum import IntEnum, StrEnum, auto
import io

from PyQt5.QtCore import QEvent, QItemSelectionModel, QModelIndex, Qt, pyqtSignal, QSize
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
    QVBoxLayout,
    QWidget,
)
from unidecode import unidecode

import util.curr_formatter as curr
from lib.Genericos.log import logging
from lib.Lancamentos.SortFilterProxy import LancamentoSortFilterProxyModel
from lib import CustomToolbar
from model.Anexos import Anexos
from model.Categoria import Categorias
from model.Conta import Conta
from model.Lancamento import Lancamentos
from model.db.db_orm import Anexos as ORMAnexos, Lancamentos as ORMLancamentos
from util.currency_editor import QCurrencyLineEdit
from util.custom_table_delegates import (
    ButtonDelegate,
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
from lib import SearchInputView, FilterInputView, ExportExcel
from view.TableLine import TableLine


class TEXTS(StrEnum):
    TITLE = "Lançamentos - (Conta {0} | {1})"
    IMPORTAR_LANCAMENTOS = "Importar Lançamentos"
    ATUALIZAR = "Atualizar"
    ELIMINAR_SEM_PERG = "Eliminar sem perguntar"
    NOVO_LANCAMENTO = "Novo Lançamento"
    ELIMINAR_SELECIONADOS = "Eliminar selecionados"
    TOTAL = "TOTAL"
    LANC_N_ENCONTRADO = "Lanc não encontrado."
    PROCURAR = 'Procurar'
    PROXIMO = 'Proximo'
    ANTERIOR = 'Anterior'
    FILTRAR = 'Filtrar'
    FILTRAR_VALOR = 'Filtrar usando "{0}"'
    REMOVE_LANCAMENTO = "Remove Lancamento?"
    REMOVE_LANCAMENTOS = "Remove Lancamentos?"
    DESEJA_REMOVER = "Deseja remover o lançamento {0} ?"
    NOVO_LANC_ADICIONADO = "Novo lançamento adicionado."
    DESEJA_REM_LANCS = "Deseja remover {0} lançamentos ?"
    ERRO = 'Erro'
    SELEC_UMA_LINHA = 'Selecionar ao menos uma linha.'
    NAO_EXISTE_CATEGORIA = "Não existe categoria com o nome {0}."
    EXPORTAR_PLANILHA = "Exportar planilha"
    EXPORTAR_PREFIXO = "Lançamentos"


class LancamentosView(MyDialog):
    # lancamento: ORMLancamentos, field:str
    changed = pyqtSignal(ORMLancamentos, str)
    # lancamento_id: int
    add_lancamento = pyqtSignal(int)
    # lancamento_id: int
    on_delete = pyqtSignal(int)

    records_added = pyqtSignal()

    class Columns(IntEnum):
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
        NR_ANEXOS = auto()

    COLUMNS = {
        Columns.ID: {"title": "ID", "sql_colname": "id", "col_width": 90 },
        Columns.SEQ_ORDEM_LINHA: { "title": "Seq Linha", "sql_colname": "seq_ordem_linha", "col_width": 100 },
        Columns.NR_REFERENCIA: { "title": "Número Ref.", "sql_colname": "nr_referencia", "col_width": 100 },
        Columns.DESCRICAO: {"title": "Descrição", "sql_colname": "descricao", "col_width": 500},
        Columns.DESCRICAO_USER: {"title": "Descrição Usuário", "sql_colname": "descricao_user", "col_width": 100},
        Columns.DATA: {"title": "Data", "sql_colname": "data", "col_width": 160},
        Columns.CATEGORIA_ID: {"title": "Categorias", "sql_colname": "categoria_id", "col_width": 260},
        Columns.VALOR: {"title": "Valor", "sql_colname": "valor", "col_width": 160},
        Columns.SALDO: {"title": "Saldo", "col_width": 160},
        Columns.REMOVER: {"title": "Remover", "col_width": 100},
        Columns.ANEXOS: {"title": "Anexos", "col_width": 100},
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
        self.filter_dialog = None
        self.total_label = TotalCurrLabel()
        self.model_lancamentos = Lancamentos(conta_dc)
        self.model_categorias = Categorias()
        self.model_categorias.load()
        self.global_settings = Settings()
        self.settings: JanelaLancamentosSettings = (
            self.global_settings.load_lanc_settings(self.conta_dc.id)
        )
        self.copied_cell: QModelIndex = None
        self.setWindowTitle(TEXTS.TITLE.format(self.conta_dc.id,self.conta_dc.descricao))
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

    def get_toolbar(self) -> CustomToolbar:
        """
        Retorna toolbar
        """
        toolbar: CustomToolbar = CustomToolbar()

        import_act = toolbar.addAction(icons.import_file(), TEXTS.IMPORTAR_LANCAMENTOS)
        import_act.triggered.connect(self.on_import_lancam)

        refresh_act = toolbar.addAction(icons.atualizar(), TEXTS.ATUALIZAR)
        refresh_act.triggered.connect(lambda: self.load_table_data())

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer)

        self.check_del_not_ask = QCheckBox(TEXTS.ELIMINAR_SEM_PERG)
        toolbar.addWidget(self.check_del_not_ask)

        add_act = toolbar.addAction(icons.add(), TEXTS.NOVO_LANCAMENTO)
        add_act.triggered.connect(lambda: self.on_add_lancamento())

        rem_act = toolbar.addAction(icons.delete(), TEXTS.ELIMINAR_SELECIONADOS)
        rem_act.triggered.connect(lambda: self.on_rem_lancamentos())
        
        toolbar.addSeparator()

        export_act = toolbar.addAction(icons.exportar_planilha(), TEXTS.EXPORTAR_PLANILHA)
        export_act.triggered.connect(lambda: self.on_export_excel())

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
        self.table.contextMenuEvent = self.call_table_ctx_menu

        return self.table

    def model_item_changed(self, item:QStandardItem):
        logging.debug(f"Item changed row: {item.row()} col: {item.column()}, Userrole: {item.data(Qt.UserRole)}")

        self.table_cell_changed(item.index())

    def call_table_ctx_menu(self, pos):
        pos = self.table.viewport().mapFromGlobal(QCursor.pos())
        self.on_table_header_context_menu(pos)

    def get_footer(self):
        """
        Retorna rodapé com total dos lancamentos
        """
        layout = QHBoxLayout()

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout.insertStretch(0)
        layout.addWidget(QLabel(TEXTS.TOTAL))
        layout.addWidget(self.total_label)

        footer = QWidget(self)
        footer.setLayout(layout)
        return footer

    def on_open_attachments(self, index:QModelIndex):
        """
        Exibe a janela de anexos
        """
        model:QStandardItemModel = index.model()
        lancamento_id: int  = model.index(index.row(), self.Columns.ID).data(Qt.UserRole)
        lancamento = self.model_lancamentos.get_lancamento(lancamento_id)
        if not lancamento:
            QMessageBox(text=TEXTS.LANC_N_ENCONTRADO).exec()
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
            self.search_dialog = SearchInputView(self)
            self.layout().insertWidget(1, self.search_dialog)
        self.search_dialog.show(col["title"], logical_index)
        self.search_dialog.on_close_signal.connect(self.on_close_search_dialog)

    def on_close_search_dialog(self):
        self.search_dialog = None

    def open_filter(self, valor:str=None):
        if not self.filter_dialog:
            self.filter_dialog = FilterInputView(self)
            self.layout().insertWidget(1, self.filter_dialog)
        if valor:
            self.filter_dialog.filter_field.setText(valor)
            self.filter_dialog.filter_button.click()
        self.filter_dialog.show()
        self.filter_dialog.on_close_signal.connect(self.on_close_filter_dialog)

    def on_close_filter_dialog(self):
        model:LancamentoSortFilterProxyModel = self.table.model() 
        model.clear_filters()
        model.invalidateFilter()
        self.filter_dialog = None

    def on_table_header_context_menu(self, point):
        hheader = self.table.horizontalHeader()
        column = self.table.indexAt(point)
        column_id = column.column()
        if column_id < 2 or column_id > 8:
            return

        menu = QMenu(self)
        menu.addAction( QAction(icons.tab_search(), TEXTS.PROCURAR, menu,  
            shortcut=QKeySequence(Qt.CTRL + Qt.Key_F), 
            triggered=lambda: self.open_search(column_id)))
        menu.addSeparator()
        menu.addAction( QAction(icons.tab_search(), TEXTS.PROXIMO, menu, 
            shortcut=QKeySequence(Qt.CTRL + Qt.Key_N), 
            triggered=lambda: self.open_search(column_id)))
        menu.addAction( QAction(icons.tab_search(), TEXTS.ANTERIOR, menu, 
            shortcut=QKeySequence(Qt.CTRL + Qt.Key_P), 
            triggered=lambda: self.open_search(column_id)))
        menu.addSeparator()
        menu.addAction( QAction(icons.tab_search(), TEXTS.FILTRAR, menu,
            shortcut=QKeySequence(Qt.CTRL + Qt.Key_L), 
            triggered=lambda: self.open_filter()))
        valor_celula = self.table.selectedIndexes()[0].data(Qt.DisplayRole)
        menu.addAction( QAction(icons.tab_search(), TEXTS.FILTRAR_VALOR.format(valor_celula), menu,
            shortcut=QKeySequence(Qt.CTRL + Qt.Key_Semicolon), 
            triggered=lambda: self.open_filter(valor_celula)))

        menu.popup(hheader.mapToGlobal(point))

    def table_cell_changed(self, index: QModelIndex):
        row = index.row()
        col = index.column()

        logging.debug(f"Cell changed row/col: {row}/{col}")

        model:LancamentoSortFilterProxyModel = self.table.model()
        col_id_index = index.model().index(row, self.Columns.ID)
        lancamento_id = model.data(model.mapFromSource(col_id_index), Qt.UserRole)
        value = model.data(model.mapFromSource(index), Qt.UserRole)

        column_data = self.COLUMNS.get(col)
        if "sql_colname" not in column_data:
            return
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
        # self.load_model_only(sql_colname == 'data')
        if sql_colname != 'categoria_id':
            self.load_model_only()
        if sql_colname == 'data':
            item_new_indexes = model.match(model.index(0, self.Columns.ID), Qt.UserRole, lancamento_id, 1)
            if len(item_new_indexes) > 0:
                item_new_index = model.index(item_new_indexes[0].row(), self.Columns.DATA)
                self.table.scrollTo(item_new_index)
                self.table.selectionModel().select(item_new_index, QItemSelectionModel.SelectCurrent)
                self.table.setCurrentIndex(item_new_index)

        lancamento: ORMLancamentos = self.model_lancamentos.get_lancamento(
            lancamento_id
        )
        self.changed.emit(lancamento, sql_colname)
        self.table.setFocus()

    def on_del_lancamento(self, index:QModelIndex):
        if not index:
            return

        model:QStandardItemModel = index.model()
        lancamento_id = model.index(index.row(), self.Columns.ID).data(Qt.UserRole)

        if not self.check_del_not_ask.isChecked():
            button = QMessageBox.question(
                self,
                TEXTS.REMOVE_LANCAMENTO,
                TEXTS.DESEJA_REMOVER.format(lancamento_id),
                buttons=QMessageBox.Yes | QMessageBox.No,
                defaultButton=QMessageBox.No,
            )
            if button == QMessageBox.No:
                return

        logging.debug(f"Eliminando lancamento {lancamento_id} do banco de dados ...")
        self.model_lancamentos.delete(str(lancamento_id))

        model.removeRow(index.row())
        self.recalculate_saldo_total()
        # self.load_model_only()

        logging.debug("Feito !!!")
        self.on_delete.emit(lancamento_id)

    def on_add_lancamento(self, show_message=True):
        logging.debug("Adicionando novo lancamento na base de dados...")
        new_lancamento_id = self.model_lancamentos.add_new_empty(self.conta_dc.id)

        logging.debug(f"Feito !!! Lancamento criado com id: {new_lancamento_id}")
        self.add_lancamento.emit(new_lancamento_id)
        self.load_model_only()
        model = self.table.model()
        items_found = model.match(model.index(0, 0), Qt.UserRole, new_lancamento_id, 1)
        if len(items_found) > 0:
            self.table.scrollTo(items_found[0])
            self.table.selectRow(items_found[0].row())

        if show_message:
            QToaster.showMessage(self, TEXTS.NOVO_LANC_ADICIONADO)

    def on_rem_lancamentos(self):
        item: QModelIndex = None
        list_of_indx = []
        for item in self.table.selectedIndexes():
            lanc_id = item.model().index(item.row(), 0).data(Qt.UserRole)
            list_of_indx.append({"index": item.row(), "id": str(lanc_id)})

        selected_count = len(list_of_indx)

        if selected_count == 0:
            QMessageBox.critical(self, TEXTS.ERRO, TEXTS.SELEC_UMA_LINHA)
            return

        pop_answer = QMessageBox.question(
            self,
            TEXTS.REMOVE_LANCAMENTOS,
            TEXTS.DESEJA_REM_LANCS.format(selected_count),
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

    def on_export_excel(self) -> None:
        model:QStandardItemModel = self.table.model().sourceModel()
        export_excel = ExportExcel(self, model, self.conta_dc.descricao)
        export_excel.export(TEXTS.EXPORTAR_PREFIXO)

    def recalculate_saldo_total(self):
        self.model_lancamentos.load()
        filter_model:LancamentoSortFilterProxyModel = self.table.model()
        model:QStandardItemModel = filter_model.sourceModel()

        saldo = 0
        for (new_index, row) in enumerate(self.model_lancamentos.items):
            saldo += row.valor
            model.setItemData(
                model.index(new_index, self.Columns.SALDO),
                {
                    Qt.DisplayRole: curr.str_curr_to_locale(saldo or 0),
                    Qt.UserRole: saldo,
                    Qt.AccessibleTextRole: saldo,
                },
            )
        # Define valor do TOTAL que aparece no rodapé da janela
        self.total_label.set_int_value(self.model_lancamentos.total)


    def load_model_only(self) -> None:
        self.model_lancamentos.load()

        filter_model:LancamentoSortFilterProxyModel = self.table.model()
        model:QStandardItemModel = filter_model.sourceModel()
        try:
            model.itemChanged.disconnect(self.model_item_changed)
        except Exception as e:
            pass # ignore error

        model.setRowCount(len(self.model_lancamentos.items))
        saldo = 0
        for (new_index, row) in enumerate(self.model_lancamentos.items):
            model.setItemData(
                model.index(new_index, self.Columns.ID),
                {Qt.UserRole: row.id},
            )
            model.setItemData(
                model.index(new_index, self.Columns.SEQ_ORDEM_LINHA),
                {Qt.UserRole: row.seq_ordem_linha},
            )
            model.setItemData(
                model.index(new_index, self.Columns.NR_REFERENCIA),
                {Qt.DisplayRole: row.nr_referencia, Qt.UserRole: row.nr_referencia},
            )
            try:
                model.setItemData(
                    model.index(new_index, self.Columns.DESCRICAO),
                    {Qt.DisplayRole: row.descricao, Qt.UserRole: row.descricao, Qt.AccessibleTextRole: unidecode(row.descricao)},
                )
            except Exception as e:
                pass

            descricao_user = row.descricao_user or ""
            model.setItemData(
                model.index(new_index, self.Columns.DESCRICAO_USER),
                {Qt.DisplayRole: descricao_user, 
                 Qt.UserRole: descricao_user, 
                 Qt.AccessibleTextRole: unidecode(descricao_user)},
            )
            model.setItemData(
                model.index(new_index, self.Columns.DATA),
                {Qt.DisplayRole: row.data.strftime("%x"), Qt.UserRole: row.data, Qt.AccessibleTextRole: row.data},
            )
            if len(row.Categorias) > 0:
                categoria = row.Categorias[0]
            else:
                categoria = self.model_categorias.items[0]
            model.setItemData(
                model.index(new_index, self.Columns.CATEGORIA_ID),
                {
                    Qt.DisplayRole: categoria.nm_categoria,
                    Qt.UserRole: categoria.id or -1,
                    Qt.AccessibleTextRole: unidecode(categoria.nm_categoria)
                },
            )
            model.setItemData(
                model.index(new_index, self.Columns.VALOR),
                {
                    Qt.DisplayRole: curr.str_curr_to_locale(row.valor or 0),
                    Qt.UserRole: row.valor or 0,
                    Qt.AccessibleTextRole: row.valor or 0,
                },
            )
            saldo += row.valor
            model.setItemData(
                model.index(new_index, self.Columns.SALDO),
                {
                    Qt.DisplayRole: curr.str_curr_to_locale(saldo or 0),
                    Qt.UserRole: saldo,
                    Qt.AccessibleTextRole: saldo,
                },
            )
            model.setItemData(
                model.index(new_index, self.Columns.ANEXOS),
                {
                    Qt.UserRole: row.nr_anexos 
                },
            )
            model.setItemData(
                model.index(new_index, self.Columns.NR_ANEXOS),
                {
                    Qt.UserRole: row.nr_anexos 
                },
            )


        filter_model.setSourceModel(model)
        self.table.setModel(filter_model)

        model.itemChanged.connect(self.model_item_changed)

        # Define valor do TOTAL que aparece no rodapé da janela
        self.total_label.set_int_value(self.model_lancamentos.total)

    def load_table_data(self):
        """ Popula tabela com os dados do modelo, redimensiona colunas """
        # reset sort order
        self.table.sortByColumn(-1, Qt.AscendingOrder)

        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        vert_scr_position = self.table.verticalScrollBar().value()

        logging.info(f"Loading lancamentos (conta id: {self.conta_dc.id}) data...")

        self.load_model_only()

        col1_del = GenericInputDelegate(self.table)
        col2_del = GenericInputDelegate(self.table)
        col3_del = self.tableline.get_date_input()
        col4_del = self.tableline.get_categoria_dropdown_delegate()
        col5_del = self.tableline.get_currency_value_delegate()
        col6_del = GenericInputDelegate(self.table)
        col7_del = ButtonDelegate(self.table, LancamentoTableLine.get_attach_button(), self.on_open_attachments)

        self.table.setItemDelegateForColumn(self.Columns.ID, IDLabelDelegate(self.table))
        self.table.setItemDelegateForColumn(self.Columns.SEQ_ORDEM_LINHA, IDLabelDelegate(self.table))
        self.table.setItemDelegateForColumn(self.Columns.NR_REFERENCIA, col1_del)
        self.table.setItemDelegateForColumn(self.Columns.DESCRICAO, col2_del)
        self.table.setItemDelegateForColumn(self.Columns.DESCRICAO_USER, col6_del)
        self.table.setItemDelegateForColumn(self.Columns.DATA, col3_del)
        self.table.setItemDelegateForColumn(self.Columns.CATEGORIA_ID, col4_del)
        self.table.setItemDelegateForColumn(self.Columns.VALOR, col5_del)
        self.table.setItemDelegateForColumn(self.Columns.SALDO, CurrencyLabelDelegate(self.table, bold=True))
        self.table.setItemDelegateForColumn(self.Columns.REMOVER, ButtonDelegate(self.table, 
            LancamentoTableLine.get_del_button(), self.on_del_lancamento) )
        self.table.setItemDelegateForColumn(self.Columns.ANEXOS, col7_del )

        self.table.verticalScrollBar().setValue(vert_scr_position)
        QApplication.restoreOverrideCursor()

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
        self.load_model_only()

    def show_all(self):
        filter_model: LancamentoSortFilterProxyModel = self.table.model()
       
        filter_model.setFilterRegExp(".*")

    def keyPressEvent(self, e:QEvent) -> None:
        if e.key() == Qt.Key_Escape:
            return

        # Evento Copiar Ctrl + C
        if e.key() == Qt.Key_C and (e.modifiers() & Qt.ControlModifier):
            self.handle_copy()
        # Evento Copiar Ctrl + V
        elif e.key() == Qt.Key_V and (e.modifiers() & Qt.ControlModifier):
            self.handle_paste()

        # Evento Ctrl + L para chamar a filtro na tabela
        if e.key() == Qt.Key_L and (e.modifiers() & Qt.ControlModifier):
            self.open_filter()

        # Evento Ctrl + ; para chamar a filtro na tabela com valor
        if e.key() == Qt.Key_Semicolon and (e.modifiers() & Qt.ControlModifier):
            valor_celula = self.table.selectedIndexes()[0].data(Qt.DisplayRole)
            self.open_filter(valor_celula)

        # Evento Ctrl + F para chamar a busca na coluna
        if e.key() == Qt.Key_F and (e.modifiers() & Qt.ControlModifier):
            index = next((sel_ind for sel_ind in self.table.selectedIndexes()), None)
            if not index:
                return

            if index.column() not in (
                self.Columns.ID,
                self.Columns.SEQ_ORDEM_LINHA,
                self.Columns.NR_REFERENCIA,
                self.Columns.DESCRICAO,
                self.Columns.DESCRICAO_USER,
                self.Columns.DATA, 
                self.Columns.CATEGORIA_ID, 
                self.Columns.VALOR, 
                self.Columns.SALDO, 
            ):
                return

            self.open_search(index.column())
            return

        if self.search_dialog:
            # evento move cursor para o registro anterior na lista encontrada 
            if e.key() == Qt.Key_P and (e.modifiers() & Qt.ControlModifier):
                self.table.clearSelection()
                self.search_dialog.on_click_search(go_prev=True)
                return

            # evento move cursor para o registro proximo na lista encontrada 
            if e.key() == Qt.Key_N and (e.modifiers() & Qt.ControlModifier):
                self.table.clearSelection()
                self.search_dialog.on_click_search()
                return

        return super(LancamentosView, self).keyPressEvent(e)

    def handle_copy(self) -> None:
        logging.debug("Copiar")
        selected = self.table.selectedIndexes()

        if selected:
            rows = sorted(index.row() for index in selected)
            columns = sorted(index.column() for index in selected)
            rowcount = rows[-1] - rows[0] + 1
            colcount = columns[-1] - columns[0] + 1
            table = [[''] * colcount for _ in range(rowcount)]
            for index in selected:
                row = index.row() - rows[0]
                column = index.column() - columns[0]
                table[row][column] = index.data()
            stream = io.StringIO()
            csv.writer(stream, delimiter='\t').writerows(table)
            QApplication.clipboard().setText(stream.getvalue()) 

    def handle_paste(self) -> None:
        selection = self.table.selectedIndexes()
        if selection:
            model = self.table.model()

            buffer = QApplication.clipboard().text() 
            rows = sorted(index.row() for index in selection)
            columns = sorted(index.column() for index in selection)
            reader = csv.reader(io.StringIO(buffer), delimiter='\t')
            if len(rows) == 1 and len(columns) == 1:
                for i, line in enumerate(reader):
                    for j, cell in enumerate(line):
                        index_to_change = model.index(rows[0]+i,columns[0]+j)

                        if index_to_change.column() == self.Columns.CATEGORIA_ID:
                            categoria = next((x for x in self.model_categorias.items 
                                if x.nm_categoria == cell), None)
                            if categoria:
                                model.setData(index_to_change, categoria.id, Qt.UserRole)
                            else:
                                QMessageBox.critical(self, TEXTS.ERRO, TEXTS.NAO_EXISTE_CATEGORIA.format(cell))
                        else: 
                            model.setData(index_to_change, cell, Qt.UserRole)
            else:
                arr = [ [ cell for cell in row ] for row in reader]
                for index in selection:
                    row = index.row() - rows[0]
                    column = index.column() - columns[0]
                    index_to_change = model.index(rows[0]+i,columns[0]+j)
                    model.setData(index_to_change, arr[row][column], Qt.UserRole)


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
    def get_del_button() -> QPushButton:
        del_pbutt = QPushButton()
        del_pbutt.setToolTip("Eliminar Lançamento")
        del_pbutt.setIcon(icons.delete())
        return del_pbutt

    @staticmethod
    def get_attach_button() -> QPushButton:
        del_pbutt = QPushButton()
        del_pbutt.setToolTip("Anexos")
        del_pbutt.setIcon(icons.attach())
        return del_pbutt
