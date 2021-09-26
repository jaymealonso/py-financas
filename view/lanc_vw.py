import locale
import datetime
import typing
import view.icons.icons as icons
import view.contas_vw as cv
from view.imp_lanc_vw import ImportarLancamentosView
from model.Conta import Conta
from model.Categoria import Categorias
from model.Lancamento import Lancamentos, Lancamento
from PyQt5.QtGui import QCloseEvent, QValidator
from PyQt5.QtCore import Qt, QObject, QRegExp, QDate, QLocale
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QLineEdit, QPushButton, QToolBar, QSizePolicy, \
    QMessageBox, QTableWidgetItem, QLabel, QComboBox, QDateEdit
from util.toaster import QToaster
from util.events import post_event, Eventos
import util.curr_formatter as curr


class LancamentosView(QWidget):
    COLUMNS = {
        0: {"title": "ID", "sql_colname": "_id"},
        1: {"title": "Número Ref.", "sql_colname": "nr_referencia"},
        2: {"title": "Descrição", "sql_colname": "descricao"},
        3: {"title": "Data", "sql_colname": "data"},
        4: {"title": "Categorias", "sql_colname": "categoria_id"},
        5: {"title": "Valor", "sql_colname": "valor"},
        6: {"title": "Remover"}
    }

    def __init__(self, parent: QWidget, conta_dc: Conta):
        self.toolbar = QToolBar()
        self.table = QTableWidget()
        self.tableline = LancamentoTableLine(self)
        self.conta_dc = conta_dc
        self.parent: cv.ContasView = parent
        self.import_lanc_view = None
        self.model_lancamentos = Lancamentos(conta_dc)
        self.model_categorias = Categorias()
        self.model_categorias.load()
        self.conta_id = conta_dc.id

        super(LancamentosView, self).__init__()

        self.setWindowTitle(f"Lançamentos - (Conta {conta_dc.id} | {conta_dc.descricao})")
        self.setMinimumSize(800, 600)
        self.resize(1600, 900)
        layout = QVBoxLayout()
        layout.addWidget(self.get_toolbar())
        layout.addWidget(self.get_table())

        self.setLayout(layout)

    def closeEvent(self, event: QCloseEvent) -> None:
        print(f"Lancamento close event INSIDE LANCAMENTOS conta: {self.conta_id}")
        post_event(Eventos.LANCAMENTO_WINDOW_CLOSED, str(self.conta_id))
        # del self.parent.lanc_windows[str(self.conta_id)]

    def get_toolbar(self):
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        # save_act = self.toolbar.addAction(icons.save(), "Salvar")
        # save_act.triggered.connect(lambda: self.on_save())
        # self.toolbar.addSeparator()

        import_act = self.toolbar.addAction(icons.import_file(), "Importar Lançamentos")
        import_act.triggered.connect(self.on_import_lancam)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar.addWidget(spacer)

        add_act = self.toolbar.addAction(icons.add(), "Novo Lançamento")
        add_act.triggered.connect(lambda: self.on_add_lancamento())

        return self.toolbar

    def on_import_lancam(self):
        self.import_lanc_view = ImportarLancamentosView(self, self.conta_dc)
        self.import_lanc_view.show()

    def get_table(self):
        self.table.setColumnCount(len(self.COLUMNS))
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalHeaderLabels([col["title"] for col in self.COLUMNS.values()])
        self.load_table_data()

        return self.table

    def table_cell_changed(self, row: int, col: int):
        lancamento_dc = self.model_lancamentos.items()[row]
        item = self.table.item(row, col)
        if item:
            value = item.text()
        else:
            widget = self.table.cellWidget(row, col)
            if not widget:
                return
            if isinstance(widget, QDateEdit):
                date = widget.date()
                value = datetime.date(date.year(), date.month(), date.day()).isoformat()
            elif isinstance(widget, QComboBox):
                value = widget.currentData()
            elif isinstance(widget, QCurrencyLineEdit):
                value = widget.to_float()

        column_data = self.COLUMNS.get(col)

        print(f"Modificando lancamento numero:{lancamento_dc.id} campo \"{column_data['sql_colname']}\" para valor \"{value}\"")
        lancamento_dc.__setattr__(column_data["sql_colname"], value)
        self.model_lancamentos.update(lancamento_dc)

        # self.load_table_data()
        self.model_lancamentos.load()
        total_value = sum([x.valor for x in self.model_lancamentos.items()])
        self.table_add_total_line(total_value, replace=True)
        self.parent.load_table_data()

    def on_del_lancamento(self, lancamento_id: int):
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
        pass

    def on_add_lancamento(self, show_message=True):
        print("Adding new lancamento in the database...")
        new_lancamento = Lancamento(
            id=None,
            conta_id=int(self.conta_id),
            nr_referencia='ref',
            descricao='descr',
            data=datetime.date.today(),
            valor=0,
            categoria_id=0
        )
        self.model_lancamentos.add_new(new_lancamento)
        print(f"Done !!! Lancamento criado com id: {new_lancamento.id}")
        post_event(Eventos.LANCAMENTO_CREATED, new_lancamento)
        self.load_table_data()
        if show_message:
            QToaster.showMessage(self, "On ADD CONTA clicked", closable=False, timeout=2000, corner=Qt.BottomRightCorner)

    def load_table_data(self):
        try:
            print("> Disconnecting table cellChanged... ", end=" ")
            self.table.cellChanged.disconnect()
            print("Disconnected!")
        except:
            print("Cellchanged not connected!")

        print(f"Loading lancamentos (conta id: {self.conta_id}) data...")
        self.model_lancamentos.load()

        # clear table
        self.table.setRowCount(0)

        total_value = 0.0
        for row in self.model_lancamentos.items():
            new_index = self.table.rowCount()
            self.table.insertRow(new_index)

            self.table.setCellWidget(new_index, 0, self.tableline.get_label_for_id(str(row.id)))
            self.table.setItem(new_index, 1, QTableWidgetItem(row.nr_referencia))
            self.table.setItem(new_index, 2, QTableWidgetItem(row.descricao))
            self.table.setCellWidget(new_index, 3, self.tableline.get_date_input(row.data, new_index, 3))
            # self.table.setItem(new_index, 4, QTableWidgetItem(str(row.categoria_id)))
            self.table.setCellWidget(new_index, 4, self.tableline.get_categorias_lanc_dropdown(row.categoria_id, new_index, 4))
            self.table.setCellWidget(new_index, 5, self.tableline.get_currency_input(row.valor, new_index, 5))
            self.table.setCellWidget(new_index, 6, self.tableline.get_del_button(self, str(row.id)))

            total_value = total_value + float(row.valor)

        # Adiciona linhe de TOTAL no final
        self.table_add_total_line(total_value)
        # new_index = self.table.rowCount()
        # self.table.insertRow(new_index)
        # self.table.setCellWidget(new_index, 5, self.tableline.get_label_for_total_curr(total_value))

        self.table.cellDoubleClicked.connect(self.on_table_cell_doubleclick)

        self.table.cellChanged.connect(self.table_cell_changed)
        print("> Cellchanged connected again!")

        # self.table.resizeColumnToContents(0)
        self.table.resizeColumnsToContents()
        self.table.setColumnWidth(6, 100)

    def table_add_total_line(self, total: float, replace=False):
        last_index = self.table.rowCount()
        if not replace:
            self.table.insertRow(last_index)
        else:
            last_index -= 1
        self.table.setCellWidget(last_index, 5, self.tableline.get_label_for_total_curr(total))

    def on_table_cell_doubleclick(self, row: int, col: int):
        if col == 4:
            item = self.model_lancamentos.items()[row]
            combobox = self.tableline.get_categorias_lanc_dropdown(item.categoria_id, row, col)
            self.table.setCellWidget(row, col, combobox)
            combobox.setEditable(True)


class LancamentoTableLine(QObject):
    def __init__(self, parent: LancamentosView):
        super(QObject, self).__init__()
        self.parentOne: LancamentosView = parent

    @staticmethod
    def get_label_for_total_curr(value: float):
        label = QLabel(curr.float_to_locale(value))
        color = "color:darkgreen"
        if value < 0:
            color = "color:red"
        stylesheet = f"margin-right:3px; margin-left:3px; font-weight:bold;{color}"
        label.setStyleSheet(stylesheet)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return label

    @staticmethod
    def get_label_for_id(value: str):
        label = QLabel(value)
        label.setStyleSheet("color:red")
        label.setAlignment(Qt.AlignCenter)
        return label

    def get_date_input(self, date: datetime.date, row:int, col:int):
        value = QDate(int(date[:4]), int(date[5:7]), int(date[8:10]))
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(value)
        date_edit.dateChanged.connect(lambda: self.parentOne.table.cellChanged.emit(row, col))

        return date_edit

    def get_currency_input(self, valor: float, row:int, col:int):
        line_edit = QCurrencyLineEdit()
        line_edit.setTextFloat(valor)
        line_edit.setAlignment(Qt.AlignRight)
        line_edit.setStyleSheet("border: none; margin-right:3px; margin-left:3px")
        line_edit.setLocale(QLocale(QLocale.Portuguese, QLocale.Brazil))
        line_edit.setValidator(QCurrencyValidator())

        # SIGNALS
        line_edit.textChanged.connect(self.on_curr_input_text_changed)
        line_edit.editingFinished.connect(lambda: self.parentOne.table_cell_changed(row, col))

        return line_edit

    def on_curr_input_text_changed(self, *args, **kwargs):
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

    def get_del_button(self, parent: LancamentosView, index):
        del_pbutt = QPushButton()
        del_pbutt.setToolTip("Eliminar Lançamento")
        del_pbutt.setIcon(icons.delete())
        del_pbutt.clicked.connect(lambda: parent.on_del_lancamento(index))
        return del_pbutt

    def get_categorias_lanc_dropdown(self, categoria_id:str, row:int, col:int):
        combobox = QComboBox()
        index: int = 0
        combobox.addItem("(vazio)", 0)
        for key, item in enumerate(self.parentOne.model_categorias.items()):
            combobox.addItem(item.nm_categoria, item.id)

        index = combobox.findData(categoria_id)
        if index == -1:
            index = 0
        combobox.setCurrentIndex(index)

        combobox.currentIndexChanged.connect(
            lambda: self.parentOne.table.cellChanged.emit(row, col))
        return combobox


class QCurrencyLineEdit(QLineEdit):
    def setTextFloat(self, a0: float) -> None:
        try:
            form_txt = locale.currency(val=a0, symbol=False, grouping=True)
        except:
            form_txt = ''
        self.setText(form_txt)

    def setText(self, a0: str) -> None:
        try:
            form_txt = curr.str_curr_to_locale(a0)
        except:
            form_txt = ''
        super(QCurrencyLineEdit, self).setText(form_txt)

    def to_float(self) -> float:
        return curr.str_curr_to_float(self.text())


class QCurrencyValidator(QValidator):
    def validate(self, a0: str, a1: int) -> typing.Tuple['QValidator.State', str, int]:
        print(f"Enter check validation a0: '{a0}', a1: '{a1}'.")

        # Check if there is a char that do not belong here
        regexp = QRegExp("[\\-0-9,. ]*")
        if not regexp.exactMatch(a0):
            print(f"VALIDATED a0: '{a0}', a1: '{a1}'. Invalid")
            return QValidator.Invalid, a0, a1

        # Check number format
        regexp = QRegExp("^-?(\\d{1,3}(\\.\\d{1,3})*|(\\d+))*(\\,)?(\\d*)?$")
        if not regexp.exactMatch(a0):
            print(f"VALIDATED NOT OK = a0: '{a0}', a1: '{a1}'. Intermediateinv ")
            try:
                a0 = self.fixup1(a0)
                return QValidator.Acceptable, a0, a1
            except:
                return QValidator.Invalid, a0, a1
        else:
            print(f"VALIDATED OK = a0: '{a0}', a1: '{a1}'. Acceptable")
            try:
                a0 = curr.str_curr_to_locale(a0)
            except:
                pass
            return QValidator.Acceptable, a0, a1

        # # return QValidator.Acceptable, a0, a1
        # return QValidator.Invalid, a0, a1

    # def str_format_number(self, str_value: str):
    #     is_negative = "-" in str_value
    #     value = str_value.replace(".", "").replace(",", ".").replace("-", "").strip()
    #     value_float = float(value)
    #     if is_negative:
    #         value_float = value_float * -1
    #     locale.setlocale(locale.LC_ALL, "pt_br")
    #     str_formatted = locale.currency(val=value_float, symbol=False, grouping=True)
    #     str_formatted = str_formatted.strip()
    #     return str_formatted

    def fixup1(self, a0: str) -> str:
        try:
            value_str = curr.str_curr_to_locale(a0)
            print(f"FIXUP a0: {a0} ==> {value_str}.")
            return value_str
        except Exception as e:
            print(f"Exception, return{a0}.")
            return a0


