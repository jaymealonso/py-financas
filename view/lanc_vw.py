import datetime
import view.icons.icons as icons
import view.contas_vw as cv
import logging
from view.imp_lanc_vw import ImportarLancamentosView
from view.TableLine import TableLine
from model.Conta import Conta
from model.Categoria import Categorias
from model.Lancamento import Lancamentos
from PyQt5.QtGui import (
    QCloseEvent,
    QStandardItemModel,
    QCursor,
    QStandardItem,
)
from PyQt5.QtCore import Qt, QObject, QModelIndex
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
)
from util.toaster import QToaster
from util.events import post_event, Eventos
from util.currency_editor import QCurrencyLineEdit
import util.curr_formatter as curr
from util.settings import Settings
from util.custom_table_delegates import (
    GenericInputDelegate,
    ComboBoxDelegate,
    DateEditDelegate,
    CurrencyEditDelegate,
)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


class LancamentosView(QWidget):
    COLUMNS = {
        0: {"title": "ID", "sql_colname": "id"},
        1: {"title": "Seq Linha", "sql_colname": "seq_ordem_linha"},
        2: {"title": "Número Ref.", "sql_colname": "nr_referencia"},
        3: {"title": "Descrição", "sql_colname": "descricao"},
        4: {"title": "Data", "sql_colname": "data"},
        5: {"title": "Categorias", "sql_colname": "categoria_id"},
        6: {"title": "Valor", "sql_colname": "valor"},
        7: {"title": "Remover"},
    }

    def __init__(self, parent: QWidget, conta_dc: Conta):
        self.toolbar = QToolBar()
        self.check_del_not_ask = QCheckBox("Eliminar sem perguntar")
        self.table = QTableView()
        self.tableline = LancamentoTableLine(self)
        self.conta_dc = conta_dc
        self.parent: cv.ContasView = parent
        self.import_lanc_view = None
        self.total_label = TotalCurrLabel()
        self.model_lancamentos = Lancamentos(conta_dc)
        self.model_categorias = Categorias()
        self.model_categorias.load()
        self.settings = Settings()

        super(LancamentosView, self).__init__()

        self.setWindowTitle(
            f"Lançamentos - (Conta {self.conta_dc.id} | {self.conta_dc.descricao})"
        )
        self.setMinimumSize(800, 600)
        if not self.settings.load_lanc_settings(self, self.conta_dc):
            self.resize(1600, 900)

        layout = QVBoxLayout()
        layout.addWidget(self.get_toolbar())
        layout.addWidget(self.get_table())
        layout.addWidget(self.get_footer())

        self.setLayout(layout)

    def get_toolbar(self):
        """
        Retorna toolbar
        """
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        import_act = self.toolbar.addAction(icons.import_file(), "Importar Lançamentos")
        import_act.triggered.connect(self.on_import_lancam)

        refresh_act = self.toolbar.addAction(icons.atualizar(), "Atualizar")
        refresh_act.triggered.connect(lambda: self.load_table_data())

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar.addWidget(spacer)

        self.toolbar.addWidget(self.check_del_not_ask)

        add_act = self.toolbar.addAction(icons.add(), "Novo Lançamento")
        add_act.triggered.connect(lambda: self.on_add_lancamento())

        return self.toolbar

    def get_table(self):
        """
        Retorna tabela com o seu layout
        """
        model = QStandardItemModel(0, len(self.COLUMNS))
        model.setHorizontalHeaderLabels([col["title"] for col in self.COLUMNS.values()])
        self.table.setModel(model)
        self.table.verticalHeader().setVisible(False)
        self.load_table_data()

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

    def closeEvent(self, event: QCloseEvent) -> None:
        logging.debug(
            f"Lancamento close event INSIDE LANCAMENTOS conta: {self.conta_dc.id}"
        )
        post_event(Eventos.LANCAMENTO_WINDOW_CLOSED, str(self.conta_dc.id))
        self.settings.save_lanc_settings(self, self.conta_dc)

    def on_import_lancam(self):
        """
        Exibe a janela de importação de lançamentos
        """
        self.import_lanc_view = ImportarLancamentosView(self, self.conta_dc)
        self.import_lanc_view.show()

    def table_cell_changed(self, item: QModelIndex):
        row = item.row()
        col = item.column()

        logging.debug(f"Cell changed row/col: {row}/{col}")
        lancamento_dc = self.model_lancamentos.items[row]
        value = item.data(Qt.UserRole)

        column_data = self.COLUMNS.get(col)

        logging.debug(
            f"Modificando lancamento numero:{lancamento_dc.id} campo \"{column_data['sql_colname']}\" para valor \"{value}\""
        )

        self.model_lancamentos.update(
            lancamento_dc.id, column_data["sql_colname"], value
        )

        self.model_lancamentos.load()
        # recalcula total
        self.total_label.set_int_value(self.model_lancamentos.total)
        self.parent.load_table_data()
        self.table.setFocus()

    def on_del_lancamento(self, lancamento_id: int):
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
        logging.debug("Done !!!")
        self.load_table_data()
        self.parent.load_table_data()

    def on_add_lancamento(self, show_message=True):
        logging.debug("Adding new lancamento in the database...")
        new_lancamento_id = self.model_lancamentos.add_new_empty(self.conta_dc.id)

        logging.debug(f"Done !!! Lancamento criado com id: {new_lancamento_id}")
        post_event(Eventos.LANCAMENTO_CREATED, new_lancamento_id)
        self.load_table_data()
        if show_message:
            QToaster.showMessage(
                self,
                "On ADD CONTA clicked",
                closable=False,
                timeout=2000,
                corner=Qt.BottomRightCorner,
            )

    def load_table_data(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        vert_scr_position = self.table.verticalScrollBar().value()
        model = self.table.model()
        try:
            logging.debug("> Disconnecting table itemChanged... ")
            model.itemChanged.disconnect()
            logging.debug("Disconnected!")
        except Exception as e:
            logging.error(f"itemChanged not connected! Error: {str(e)}")

        logging.debug(f"Loading lancamentos (conta id: {self.conta_dc.id}) data...")
        self.model_lancamentos.load()

        # clear table
        model.setRowCount(0)

        for row in self.model_lancamentos.items:
            new_index: int = model.rowCount()
            model.insertRow(new_index)

            self.table.setIndexWidget(
                model.index(new_index, 0), self.tableline.get_label_for_id(str(row.id))
            )
            self.table.setIndexWidget(
                model.index(new_index, 1),
                self.tableline.get_label_for_id(str(row.seq_ordem_linha)),
            )
            model.setItemData(
                model.index(new_index, 2),
                {Qt.DisplayRole: row.nr_referencia, Qt.UserRole: row.nr_referencia},
            )
            model.setItemData(
                model.index(new_index, 3),
                {Qt.DisplayRole: row.descricao, Qt.UserRole: row.descricao},
            )
            model.setItemData(
                model.index(new_index, 4),
                {Qt.DisplayRole: row.data.strftime("%x"), Qt.UserRole: row.data},
            )
            if len(row.Categorias) > 0:
                categoria = row.Categorias[0]
            else:
                categoria = self.model_categorias.items[0]
            model.setItemData(
                model.index(new_index, 5),
                {
                    Qt.DisplayRole: categoria.nm_categoria,
                    Qt.UserRole: categoria.id or 0,
                },
            )
            model.setItemData(
                model.index(new_index, 6),
                {
                    Qt.DisplayRole: curr.str_curr_to_locale(str(row.valor or 0)),
                    Qt.UserRole: row.valor or 0,
                },
            )

            self.table.setIndexWidget(
                model.index(new_index, 7),
                self.tableline.get_del_button(self, str(row.id)),
            )

        col1_del = GenericInputDelegate(self.table)
        col1_del.changed.connect(self.on_model_item_changed)
        col2_del = GenericInputDelegate(self.table)
        col2_del.changed.connect(self.on_model_item_changed)
        col3_del = self.tableline.get_date_input()
        col3_del.changed.connect(self.on_model_item_changed)
        col4_del = self.tableline.get_tipo_conta_dropdown_delegate()
        col4_del.changed.connect(self.on_model_item_changed)
        col5_del = self.tableline.get_currency_value_delegate()
        col5_del.changed.connect(self.on_model_item_changed)

        self.table.setItemDelegateForColumn(2, col1_del)
        self.table.setItemDelegateForColumn(3, col2_del)
        self.table.setItemDelegateForColumn(4, col3_del)
        self.table.setItemDelegateForColumn(5, col4_del)
        self.table.setItemDelegateForColumn(6, col5_del)

        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(1)
        self.table.resizeColumnToContents(2)
        self.table.resizeColumnToContents(3)
        self.table.setColumnWidth(4, 160)
        self.table.setColumnWidth(5, 260)
        self.table.setColumnWidth(6, 160)
        self.table.setColumnWidth(7, 100)

        # Define valor do TOTAL que aparece no rodapé da janela
        self.total_label.set_int_value(self.model_lancamentos.total)

        logging.debug("> itemChanged connected again!")
        self.table.verticalScrollBar().setValue(vert_scr_position)
        QApplication.restoreOverrideCursor()

    def on_model_item_changed(self, item: QStandardItem):
        """
        Disparado pela modificação de um WIDGET na linha da tabela
        """
        self.table_cell_changed(item)

    # def on_table_cell_doubleclick(self, row: int, col: int):
    #     if col == 4:
    #         item = self.model_lancamentos.items[row]
    #         combobox = self.tableline.get_categorias_lanc_dropdown(
    #             item.categoria_id, row, col
    #         )
    #         self.table.setCellWidget(row, col, combobox)
    #         combobox.setEditable(True)


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

    def get_tipo_conta_dropdown_delegate(self):
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

        # # SIGNALS
        # line_edit.textChanged.connect(self.on_curr_input_text_changed)
        # line_edit.editingFinished.connect(
        #     lambda: self.parentOne.table_cell_changed(row, col)
        # )

        return line_edit

    def on_curr_input_text_changed(self, *args, **kwargs):
        self.sender().setTextFormat()

    @staticmethod
    def get_del_button(parent: LancamentosView, index):
        del_pbutt = QPushButton()
        del_pbutt.setToolTip("Eliminar Lançamento")
        del_pbutt.setIcon(icons.delete())
        del_pbutt.clicked.connect(lambda: parent.on_del_lancamento(index))
        return del_pbutt

    # def get_categorias_lanc_dropdown(self, categoria_id: str, row: int, col: int):
    #     combobox = ComboBoxDelegate()
    #     for key, item in enumerate(self.parentOne.model_categorias.items):
    #         combobox.addItem(item.nm_categoria, item.id)

    #     index = int(combobox.findData(categoria_id))
    #     if index == -1:
    #         index = 0
    #     combobox.setCurrentIndex(index)

    #     model = self.parentOne.table.model()
    #     combobox.currentIndexChanged.connect(lambda: model.itemChanged(row, col))
    #     return combobox
