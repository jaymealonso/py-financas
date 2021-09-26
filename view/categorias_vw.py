import view.icons.icons as icons
from view.TableLine import TableLine
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QToolBar, QTableWidget, QTableWidgetItem, QComboBox, \
   QLineEdit, QPushButton, QLabel, QMainWindow, QMessageBox
from model.Categoria import Categoria, Categorias


class CategoriasView(QWidget):
    COLUMNS = {
        0: {"title": "ID", "sql_colname": "_id"},
        1: {"title": "Categoria", "sql_colname": "nm_categoria"}
    }

    def __init__(self):
        super(CategoriasView, self).__init__()

        layout = QVBoxLayout()

        self.toolbar: QToolBar = None
        self.table: QTableWidget = None
        self.model_categ = Categorias()

        layout.addWidget(self.get_toolbar())
        layout.addWidget(self.get_table())

        self.setLayout(layout)

    def get_toolbar(self):
        self.toolbar = QToolBar()
        add_act = self.toolbar.addAction(icons.add(), "Adicionar Categoria")
        add_act.triggered.connect(lambda: self.on_add_categoria())
        # self.toolbar.addSeparator()
        # refresh_act = self.toolbar.addAction(icons.atualizar(), "Atualizar")
        # refresh_act.triggered.connect(lambda: self.load_table_data())

        return self.toolbar

    def on_add_categoria(self):
        self.model_categ.add_new(Categoria(id=None, nm_categoria="Nova Categoria"))

    def get_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.COLUMNS))
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalHeaderLabels([col["title"] for col in self.COLUMNS.values()])
        self.load_table_data()

        return self.table

    def load_table_data(self):
        try:
            print("> Disconnecting table cellChanged... ", end=" ")
            self.table.cellChanged.disconnect()
            print("Disconnected!")
        except:
            print("Cellchanged not connected!")

        print("Loading categorias data...")
        self.model_categ.load()

        # Limpa a tabela
        self.table.setRowCount(0)

        line = CategoriasLine()

        for row in self.model_categ.items():
            new_index = self.table.rowCount()
            self.table.insertRow(new_index)

            # self.table.setItem(new_index, 0, QTableWidgetItem(str(row.id)))
            self.table.setCellWidget(new_index, 0, line.get_label_for_id(str(row.id)))
            self.table.setItem(new_index, 1, QTableWidgetItem(row.nm_categoria))

        self.table.resizeColumnToContents(0)
        self.table.setColumnWidth(1, 300)


class CategoriasLine(TableLine):
    def nada(self):
        pass


