from enum import StrEnum
import PyQt5.QtGui as QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QWidget, QVBoxLayout, QSizePolicy, QSplitter
from lib import CustomToolbar
from lib.VisaoMensal.Table import VisaoGeralTableView

from util import CurrencyLabelDelegate, IDLabelDelegate, MyDialog, JanelaVisaoMensalSettings, Settings
from lib.Genericos.log import logging
from lib import ExportExcel
import view.contas_vw as cv
import view.icons.icons as icons
from lib.VisaoMensal.TableLine import VisaoGeralViewLine
from model import Conta, VisaoMensal
from util.curr_formatter import str_curr_to_locale
from view.lanc_vw import LancamentosView


class TEXTS(StrEnum):
    TITLE = "Visão Mensal - (Conta {0})"
    EXPORTAR_PREFIXO = "Visão Mensal"
    LIMPAR_FILTRO = "Limpar filtro"
    TOTAL = "TOTAL"


class VisaoGeralView(MyDialog):
    def __init__(self, parent: QWidget, conta_dc: Conta):
        self.toolbar: CustomToolbar = None
        self.toolbar_vis_geral: CustomToolbar = None
        self.table: VisaoGeralTableView = None
        self.line = VisaoGeralViewLine()
        self.conta_dc = conta_dc
        self.model_visao_mensal = VisaoMensal(self.conta_dc)
        self.parent: cv.ContasView = parent
        self.global_settings = Settings()
        self.settings: JanelaVisaoMensalSettings = self.global_settings.load_visaomensal_settings(self.conta_dc.id)

        super(VisaoGeralView, self).__init__(parent)
        self.on_close_signal.connect(self.on_close)

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle(TEXTS.TITLE.format(conta_dc.id))
        self.setMinimumSize(800, 600)
        try:
            self.restoreGeometry(self.settings.dimensoes)
        except Exception as e:
            logging.error(str(e))
            self.resize(1600, 900)

        layout = QVBoxLayout()
        layout.addWidget(self.get_toolbar())

        self.splitter = QSplitter(self)
        self.splitter.addWidget(self.get_visao_geral())
        self.lancamentos_vw = self.get_lancamentos()
        self.splitter.addWidget(self.lancamentos_vw)

        try:
            splisizes: list[int] = self.settings.divisoes
        except Exception as e:
            logging.error(str(e))
            splisize = int(self.size().width() / 2)
            splisizes: list[int] = [splisize, splisize]
        finally:
            self.splitter.setSizes(splisizes)

        layout.addWidget(self.splitter)

        self.load_table_data()

        self.setLayout(layout)

    def on_close(self):
        self.settings.dimensoes = self.saveGeometry()
        self.settings.divisoes = self.splitter.sizes()

    def get_toolbar(self) -> CustomToolbar:
        if self.toolbar is None:
            self.toolbar = CustomToolbar()

            self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

            refresh_act = self.toolbar.addAction(icons.atualizar(), "Atualizar")
            refresh_act.triggered.connect(lambda: self.load_table_data())

            spacer = QWidget()
            spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.toolbar.addWidget(spacer)

            btn_exportar_planilha = self.toolbar.addAction(icons.exportar_planilha(), "Exportar")
            btn_exportar_planilha.triggered.connect(self.on_exportar_planilha)

        return self.toolbar

    def on_exportar_planilha(self):
        export_excel = ExportExcel(self, self.table.model(), self.conta_dc.descricao)
        export_excel.export(TEXTS.EXPORTAR_PREFIXO)

    def get_table(self) -> VisaoGeralTableView:
        """Tabela de visão mensal"""
        if self.table is None:
            self.table = VisaoGeralTableView(self)
            self.table.selection_released.connect(self.on_selection_released)
        return self.table

    def on_selection_released(self, filters: list):
        if self.lancamentos_vw.filter_dialog:
            self.lancamentos_vw.filter_dialog.on_fechar_popup()
        if self.lancamentos_vw.search_dialog:
            self.lancamentos_vw.search_dialog.on_fechar_popup()
        self.lancamentos_vw.set_filter_mes_categ(filters)
        self.get_limpar_filtro_button().setVisible(len(filters) > 0)

    def get_visao_geral(self) -> QWidget:
        panel = QWidget(self)
        layout = QVBoxLayout()
        layout.addWidget(self.get_toolbar_vis_geral())
        layout.addWidget(self.get_table())
        panel.setLayout(layout)

        return panel

    def get_toolbar_vis_geral(self) -> CustomToolbar:
        if self.toolbar_vis_geral is None:
            self.toolbar_vis_geral = CustomToolbar()

            self.toolbar_vis_geral.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

            spacer = QWidget()
            spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.toolbar_vis_geral.addWidget(spacer)

            btn_clear_filter = self.toolbar_vis_geral.addAction(icons.filter_clear(), TEXTS.LIMPAR_FILTRO)
            btn_clear_filter.setVisible(False)
            btn_clear_filter.triggered.connect(self.on_limpar_filtro)

        return self.toolbar_vis_geral

    def on_limpar_filtro(self):
        if self.lancamentos_vw.filter_dialog:
            self.lancamentos_vw.filter_dialog.on_fechar_popup()
        if self.lancamentos_vw.search_dialog:
            self.lancamentos_vw.search_dialog.on_fechar_popup()
        self.table.selectionModel().clear()
        self.lancamentos_vw.set_filter_mes_categ([])
        self.get_limpar_filtro_button().setVisible(False)

    def get_limpar_filtro_button(self) -> QAction:
        actions = self.toolbar_vis_geral.actions()
        return next(act for act in actions if act.iconText() == "Limpar filtro")

    def get_lancamentos(self) -> LancamentosView:
        """Janela de descricao de lancamentos"""
        lancamentos = LancamentosView(self, self.conta_dc)
        lancamentos.changed.connect(self.load_table_data)
        lancamentos.add_lancamento.connect(self.load_table_data)
        lancamentos.on_close_signal.connect(self.load_table_data)
        lancamentos.on_delete.connect(self.load_table_data)
        lancamentos.records_added.connect(self.load_table_data)
        return lancamentos

    def load_table_data(self):
        # reset sort order
        self.table.sortByColumn(-1, Qt.AscendingOrder)
        self.load_model_only()

        for index, label in enumerate(self.header_labels):
            if index == 0:
                self.table.setItemDelegateForColumn(index, IDLabelDelegate(self.table))
            else:
                self.table.setItemDelegateForColumn(index, CurrencyLabelDelegate(self.table))

    def load_model_only(self):
        self.model_visao_mensal.load()

        self.categorias_labels = self.model_visao_mensal.get_unique_row_labels()
        model = QtGui.QStandardItemModel(len(self.categorias_labels) + 1, len(self.model_visao_mensal.columns) + 1)
        self.header_labels = [col.ano_mes for col in self.model_visao_mensal.columns]
        self.header_labels.insert(0, "Categoria")
        model.setHorizontalHeaderLabels(self.header_labels)

        # set labels in the table
        self.table.set_labels(self.header_labels, self.categorias_labels)

        # first col
        for key, row_label in enumerate(self.categorias_labels):
            model.setItemData(
                model.index(key, 0), {Qt.DisplayRole: row_label or "(vazio)", Qt.UserRole: row_label or "(vazio)"}
            )
        # cell valores
        row_index = 0
        for cell in self.model_visao_mensal.values:
            col_index = self.header_labels.index(cell.ano_mes)
            row_index = self.categorias_labels.index(cell.nm_categoria)
            model.setItemData(
                model.index(row_index, col_index),
                {Qt.DisplayRole: str_curr_to_locale(cell.valor or 0), Qt.UserRole: cell.valor},
            )

        # total last row
        row_index += 1
        font = QtGui.QFont()
        font.setBold(True)
        for key, col_label in enumerate(self.header_labels):
            if key < 1:
                model.setItemData(
                    model.index(row_index, key),
                    {Qt.DisplayRole: TEXTS.TOTAL, Qt.UserRole: TEXTS.TOTAL, Qt.FontRole: font},
                )
                continue

            total = sum([cell.valor for cell in self.model_visao_mensal.values if cell.ano_mes == col_label])
            model.setItemData(
                model.index(row_index, key),
                {Qt.DisplayRole: str_curr_to_locale(total or 0), Qt.UserRole: total, Qt.FontRole: font},
            )

        self.table.setModel(model)
