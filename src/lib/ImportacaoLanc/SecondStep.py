#!

from enum import IntEnum, auto
from typing import cast

from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import QModelIndex, Qt, pyqtSignal
from PyQt5.QtWidgets import QAbstractItemView, QPushButton, QSizePolicy, QTableView, QVBoxLayout, QWidget

from lib.Genericos.QMessageHelper import MyMessagePopup
from lib.ImportacaoLanc.AddCategoriaPopup import AddCategoriasPopup
from lib import CustomToolbar, logging
from lib.ImportacaoLanc.Classification import LancamentosClassificador, TrainingData
import util.curr_formatter as curr
from util import ButtonDelegate
from lib.ImportacaoLanc.FirstStep import NewLancamento
import view.icons.icons as icons
from model import Categorias, Lancamentos

ToolButtonStyle = Qt.ToolButtonStyle
ItemDataRole = Qt.ItemDataRole


class SecondStepFrame(QWidget):
    import_linhas = pyqtSignal(list)
    """
    Envia um sinal com as linhas que devem ser importadas

    Parameters
    ----------
    lancamento_list = list[NewLancamento]
        Lista de lancçamentos a serem processados
    """

    passo_anterior = pyqtSignal()
    """Volta para o passo anterior"""

    class Column(IntEnum):
        NR_REFERENCIA = 0
        DESCRICAO = auto()
        DESCRICAO_USER = auto()
        DATA = auto()
        CATEGORIA_ID = auto()
        BTN_MOVE_CATEG = auto()
        CATEG_SUGERIDA = auto()
        VALOR = auto()
        NEW_ID = auto()
        MESSAGE = auto()

    COLUMNS = {
        Column.NR_REFERENCIA: {"title": "Número Ref.", "sql_colname": "nr_referencia", "col_width": 100},
        Column.DESCRICAO: {"title": "Descrição", "sql_colname": "descricao", "col_width": 500},
        Column.DESCRICAO_USER: {"title": "Descrição Usuário", "sql_colname": "descricao_user", "col_width": 100},
        Column.DATA: {"title": "Data", "sql_colname": "data", "col_width": 160},
        Column.CATEGORIA_ID: {"title": "Categorias", "sql_colname": "categoria_id", "col_width": 260},
        Column.BTN_MOVE_CATEG: {"title": "Aceitar", "sql_colname": "", "col_width": 100},
        Column.CATEG_SUGERIDA: {"title": "Categoria Sugerida", "sql_colname": "", "col_width": 100},
        Column.VALOR: {"title": "Valor", "sql_colname": "valor", "col_width": 160},
        Column.NEW_ID: {"title": "Novo ID", "sql_colname": "id", "col_width": 90},
        Column.MESSAGE: {"title": "Mensagem de importação", "sql_colname": "", "col_width": 600},
    }

    def __init__(self, parent: QWidget) -> None:
        super(SecondStepFrame, self).__init__(parent)

        # local vars
        self.parent_view = parent
        self.table = self.get_table()
        self.toolbar = self.get_toolbar()
        self.linhas: list[NewLancamento] = []
        self.classificador: LancamentosClassificador

        # layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.table)

        self.setLayout(layout)

        # model
        self.model_categorias = Categorias()
        self.model_categorias.load()
        self.model_lancamentos = Lancamentos()

        self.parent_view.importacao_finalizada.connect(self.set_linhas)

    def get_toolbar(self) -> CustomToolbar:
        toolbar = CustomToolbar()
        toolbar.setToolButtonStyle(ToolButtonStyle.ToolButtonTextBesideIcon)

        btn_previous = toolbar.addAction(icons.results_prev(), "Passo anterior")
        assert btn_previous is not None
        btn_previous.triggered.connect(self.passo_anterior.emit)

        btn_criar_categ = toolbar.addAction(icons.add(), "Criar categorias")
        assert btn_criar_categ is not None
        btn_criar_categ.triggered.connect(self.on_criar_categorias)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer)

        btn_import_lanc = toolbar.addAction(icons.excel_imports(), "Importar linhas")
        assert btn_import_lanc is not None
        btn_import_lanc.triggered.connect(self.on_import_linhas)

        return toolbar

    def get_table(self) -> QTableView:
        """
        Retorna tabela com o seu layout
        """
        self.table = QTableView()

        model = QStandardItemModel(0, len(self.COLUMNS))
        model.setHorizontalHeaderLabels([str(col["title"]) for col in self.COLUMNS.values()])

        self.table.setModel(model)
        self.table.setSortingEnabled(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        return self.table

    def load_table_data(self):
        # reset sort order
        self.table.sortByColumn(-1, Qt.AscendingOrder)

        self.load_model_only()

        col7_del = ButtonDelegate(self.table, self.get_accept_button(), self.on_aceita_categ_sugg)

        self.table.setItemDelegateForColumn(self.Column.BTN_MOVE_CATEG, col7_del)

        self.set_column_default_sizes()

    def on_aceita_categ_sugg(self, index: QModelIndex):
        val_sugg = index.siblingAtColumn(self.Column.CATEG_SUGERIDA)

        nm_categoria = val_sugg.data(ItemDataRole.DisplayRole)
        categ_id = next((item.id for item in self.model_categorias.items if item.nm_categoria == nm_categoria), None)
        if categ_id:
            self.linhas[index.row()].categoria_id = categ_id

        self.load_model_only()

    def get_accept_button(self) -> QPushButton:
        del_pbutt = QPushButton()
        del_pbutt.setToolTip("Aceita categoria")
        del_pbutt.setIcon(icons.arrow_left())
        return del_pbutt

    def load_model_only(self):
        model = cast(QStandardItemModel, self.table.model())
        model.setRowCount(len(self.linhas))
        vertical_col_indexes = []
        for new_index, row in enumerate(self.linhas):
            vertical_col_indexes.append(str(row.row_index))
            model.setItemData(
                model.index(new_index, self.Column.NR_REFERENCIA),
                {ItemDataRole.DisplayRole: row.nr_referencia, ItemDataRole.UserRole: row.nr_referencia},
            )
            model.setItemData(
                model.index(new_index, self.Column.DESCRICAO),
                {ItemDataRole.DisplayRole: row.descricao, ItemDataRole.UserRole: row.descricao},
            )
            model.setItemData(
                model.index(new_index, self.Column.DESCRICAO_USER),
                {ItemDataRole.DisplayRole: row.descricao_user, ItemDataRole.UserRole: row.descricao_user},
            )
            try:
                data = row.data.strftime("%x")
            except:  # noqa: E722
                data = "Inválida"
            model.setItemData(
                model.index(new_index, self.Column.DATA),
                {ItemDataRole.DisplayRole: data, ItemDataRole.UserRole: row.data},
            )
            nm_categoria = next(
                (x.nm_categoria for x in self.model_categorias.items if x.id == row.categoria_id),
                "Erro: Categoria não encontrada",
            )
            model.setItemData(
                model.index(new_index, self.Column.CATEGORIA_ID),
                {ItemDataRole.DisplayRole: nm_categoria},
            )
            model.setItemData(
                model.index(new_index, self.Column.CATEG_SUGERIDA),
                {ItemDataRole.DisplayRole: row.suggested_categ},
            )

            model.setItemData(
                model.index(new_index, self.Column.VALOR),
                {
                    ItemDataRole.DisplayRole: curr.str_curr_to_locale(row.valor or 0),
                    ItemDataRole.UserRole: row.valor or 0,
                },
            )
            model.setItemData(
                model.index(new_index, self.Column.NEW_ID),
                {ItemDataRole.DisplayRole: row.id},
            )
            model.setItemData(
                model.index(new_index, self.Column.MESSAGE),
                {ItemDataRole.DisplayRole: row.message, Qt.DecorationRole: row.icon},
            )

        model.setVerticalHeaderLabels(vertical_col_indexes)
        self.table.setModel(model)

    def set_column_default_sizes(self):
        for index, col in self.COLUMNS.items():
            self.table.setColumnWidth(index, col.get("col_width"))

    def set_linhas(self, linhas: list[NewLancamento]):
        self.linhas = linhas

        self.model_lancamentos.load(self.parent_view.conta_dc.id)
        train_data = []
        for item in self.model_lancamentos.items:
            if len(item.Categorias) > 0:
                nm_categoria = item.Categorias[0].nm_categoria
            else:
                nm_categoria = ""
            train_data.append(TrainingData(str(item.descricao), float(item.valor / 100), nm_categoria))
        self.classificador = LancamentosClassificador()
        self.classificador.train_model(train_data)

        for index, linha in enumerate(self.linhas):
            descr, prob = self.classificador.predict_category(linha.descricao, linha.valor)
            logging.debug(f"Linha {index} Sugestão: {descr} / id:{prob}")

            linha.suggested_categ = descr

        self.load_table_data()

    def on_import_linhas(self) -> None:
        """Gera lançamentos a partir das linhas selecionadas"""
        self.import_linhas.emit(self.linhas)

    def on_criar_categorias(self):
        """Chama popup de criação de categorias"""

        values = set()
        linha: NewLancamento = None
        for linha in self.linhas:
            if linha.new_categoria.strip() != "":
                values.add(linha.new_categoria)
        if len(values) == 0:
            MyMessagePopup(self).error("Nenhuma categoria nova detectada.")
            return

        popup = AddCategoriasPopup(self, values)
        popup.categ_created.connect(self.passo_anterior.emit)
        popup.open()
