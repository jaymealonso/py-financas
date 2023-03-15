from view.TableLine import TableLine
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QTableView, QVBoxLayout
from model.db.db_orm import Lancamentos as ORMLancamentos
from model.Anexos import Anexos


class AnexosView(QWidget):
    COLUMNS = {
        0: {"title": "id", "sql_colname": "id"},
        1: {"title": "descricao", "sql_colname": "descricao"},
        2: {"title": "caminho", "sql_colname": "caminho"},
        3: {"title": "Visualizar"},
    }

    def __init__(self, parent: QWidget, lancamento: ORMLancamentos):
        self.lancamento = lancamento
        self.table = self.initialize_table()
        self.tableline = AnexoTableLine(self)
        self.model_anexos = Anexos(lancamento.id)

        super(AnexosView, self).__init__()

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle("Anexos")

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.model_anexos.load()
        self.load_table_data()

    def initialize_table(self) -> QTableView:
        """
        Retorna tabela com o seu layout
        """
        table = QTableView()
        model = QStandardItemModel(0, len(self.COLUMNS))
        model.setHorizontalHeaderLabels([col["title"] for col in self.COLUMNS.values()])
        table.setModel(model)
        table.verticalHeader().setVisible(False)
        return table

    def load_table_data(self) -> None:
        """
        Popula tabela com os dados do modelo, redimensiona colunas
        """
        model = self.table.model()

        for row in self.model_anexos.items:
            new_index: int = model.rowCount()
            model.insertRow(new_index)

            self.table.setIndexWidget(
                model.index(new_index, 0),
                self.tableline.get_label_for_id(str(row.id)),
            )

            model.setItemData(
                model.index(new_index, 1),
                {Qt.DisplayRole: row.descricao, Qt.UserRole: row.descricao},
            )

            model.setItemData(
                model.index(new_index, 1),
                {Qt.DisplayRole: row.caminho, Qt.UserRole: row.caminho},
            )

        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(1)
        self.table.resizeColumnToContents(2)


class AnexoTableLine(TableLine):
    def __init__(self, parent: AnexosView):
        super(AnexoTableLine, self).__init__()
        self.parent: AnexosView = parent
