import datetime
import view.icons.icons as icons
import view.contas_vw as cv
from view.imp_lanc_vw import ImportarLancamentosView
from view.TableLine import TableLine
from model.Conta import Conta
from model.Categoria import Categorias
from model.Lancamento import Lancamentos, Lancamento
from PyQt5.QtGui import (
    QCloseEvent,
    QValidator,
    QStandardItemModel,
    QCursor,
    QStandardItem,
)
from PyQt5.QtCore import Qt, QObject, QRegExp, QDate, QLocale, QModelIndex
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QTableView,
    QLineEdit,
    QPushButton,
    QToolBar,
    QSizePolicy,
    QMessageBox,
    QLabel,
    QComboBox,
    QDateEdit,
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


class LancamentosView(QWidget):
    COLUMNS = {
        0: {"title": "ID", "sql_colname": "_id"},
        1: {"title": "Número Ref.", "sql_colname": "nr_referencia"},
        2: {"title": "Descrição", "sql_colname": "descricao"},
        3: {"title": "Data", "sql_colname": "data"},
        4: {"title": "Categorias", "sql_colname": "categoria_id"},
        5: {"title": "Valor", "sql_colname": "valor"},
        6: {"title": "Remover"},
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

    def get_footer(self):
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
        print(f"Lancamento close event INSIDE LANCAMENTOS conta: {self.conta_dc.id}")
        post_event(Eventos.LANCAMENTO_WINDOW_CLOSED, str(self.conta_dc.id))
        self.settings.save_lanc_settings(self, self.conta_dc)

    def get_toolbar(self):
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

    def on_import_lancam(self):
        self.import_lanc_view = ImportarLancamentosView(self, self.conta_dc)
        self.import_lanc_view.show()

    def get_table(self):
        model = QStandardItemModel(0, len(self.COLUMNS))
        model.setHorizontalHeaderLabels([col["title"] for col in self.COLUMNS.values()])
        self.table.setModel(model)
        self.table.verticalHeader().setVisible(False)
        self.load_table_data()

        return self.table

    def table_cell_changed(self, item: QModelIndex):
        row = item.row()
        col = item.column()

        lancamento_dc = self.model_lancamentos.items()[row]
        print(f"Cell changed row/col: {row}/{col}")
        value = item.data(Qt.UserRole)

        column_data = self.COLUMNS.get(col)

        print(
            f"Modificando lancamento numero:{lancamento_dc.id} campo \"{column_data['sql_colname']}\" para valor \"{value}\""
        )
        lancamento_dc.__setattr__(column_data["sql_colname"], value)
        self.model_lancamentos.update(lancamento_dc)

        self.model_lancamentos.load()
        total_value = sum([x.valor for x in self.model_lancamentos.items()])
        self.total_label.set_int_value(total_value)
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

        print(f"Eliminando lancamento {lancamento_id} do banco de dados ...")
        self.model_lancamentos.delete(str(lancamento_id))
        print("Done !!!")
        self.load_table_data()
        self.parent.load_table_data()

    def on_add_lancamento(self, show_message=True):
        print("Adding new lancamento in the database...")
        new_lancamento = Lancamento(
            id=None,
            conta_id=int(self.conta_dc.id),
            nr_referencia="ref",
            descricao="descr",
            data=datetime.date.today(),
            valor=0,
            categoria_id=0,
        )
        self.model_lancamentos.add_new(new_lancamento)
        print(f"Done !!! Lancamento criado com id: {new_lancamento.id}")
        post_event(Eventos.LANCAMENTO_CREATED, new_lancamento)
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
            print("> Disconnecting table itemChanged... ", end=" ")
            model.itemChanged.disconnect()
            print("Disconnected!")
        except:
            print("itemChanged not connected!")

        print(f"Loading lancamentos (conta id: {self.conta_dc.id}) data...")
        self.model_lancamentos.load()

        # clear table
        model.setRowCount(0)

        total_value: int = 0

        for row in self.model_lancamentos.items():
            new_index = model.rowCount()
            model.insertRow(new_index)

            self.table.setIndexWidget(
                model.index(new_index, 0), self.tableline.get_label_for_id(str(row.id))
            )
            model.setItemData(
                model.index(new_index, 1),
                {Qt.DisplayRole: row.nr_referencia, Qt.UserRole: row.nr_referencia},
            )
            model.setItemData(
                model.index(new_index, 2),
                {Qt.DisplayRole: row.descricao, Qt.UserRole: row.descricao},
            )
            model.setItemData(
                model.index(new_index, 3),
                {Qt.DisplayRole: row.data.strftime("%x"), Qt.UserRole: row.data},
            )
            model.setItemData(
                model.index(new_index, 4),
                {
                    Qt.DisplayRole: self.model_categorias[row.categoria_id or 0],
                    Qt.UserRole: row.categoria_id or 0,
                },
            )
            model.setItemData(
                model.index(new_index, 5),
                {
                    Qt.DisplayRole: curr.str_curr_to_locale((row.valor or 0).__str__()),
                    Qt.UserRole: row.valor or 0,
                },
            )

            self.table.setIndexWidget(
                model.index(new_index, 6),
                self.tableline.get_del_button(self, str(row.id)),
            )

            total_value = total_value + row.valor

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

        self.table.setItemDelegateForColumn(1, col1_del)
        self.table.setItemDelegateForColumn(2, col2_del)
        self.table.setItemDelegateForColumn(3, col3_del)
        self.table.setItemDelegateForColumn(4, col4_del)
        self.table.setItemDelegateForColumn(5, col5_del)

        # Adiciona linha de TOTAL no final
        self.total_label.set_int_value(total_value)

        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(1)
        self.table.resizeColumnToContents(2)
        self.table.setColumnWidth(3, 160)
        self.table.setColumnWidth(4, 260)
        self.table.setColumnWidth(5, 160)
        self.table.setColumnWidth(6, 100)

        # model.itemChanged.connect(self.on_model_item_changed)
        print("> itemChanged connected again!")
        self.table.verticalScrollBar().setValue(vert_scr_position)
        QApplication.restoreOverrideCursor()

    def on_model_item_changed(self, item: QStandardItem):
        self.table_cell_changed(item)

    def on_table_cell_doubleclick(self, row: int, col: int):
        if col == 4:
            item = self.model_lancamentos.items()[row]
            combobox = self.tableline.get_categorias_lanc_dropdown(
                item.categoria_id, row, col
            )
            self.table.setCellWidget(row, col, combobox)
            combobox.setEditable(True)


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
        categorias = {0: "(vazio)"}
        for item in self.parentOne.model_categorias.items():
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

    def get_categorias_lanc_dropdown(self, categoria_id: str, row: int, col: int):
        combobox = ComboBoxDelegate()
        combobox.addItem("(vazio)", 0)
        for key, item in enumerate(self.parentOne.model_categorias.items()):
            combobox.addItem(item.nm_categoria, item.id)

        index = int(combobox.findData(categoria_id))
        if index == -1:
            index = 0
        combobox.setCurrentIndex(index)

        model = self.parentOne.table.model()
        combobox.currentIndexChanged.connect(lambda: model.itemChanged(row, col))
        return combobox
