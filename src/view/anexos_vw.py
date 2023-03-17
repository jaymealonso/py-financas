import os.path
import shutil
from pathlib import Path
import view.icons.icons as icons
from view.TableLine import TableLine
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import QWidget, QTableView, QVBoxLayout, QDialog, \
    QPushButton, QMessageBox, QLineEdit, QHBoxLayout, QLabel, QFileDialog 
from model.db.db_orm import Lancamentos as ORMLancamentos
from model.Anexos import Anexos


class AnexosView(QDialog):
    COLUMNS = {
        0: {"title": "id", "sql_colname": "id"},
        1: {"title": "descricao", "sql_colname": "descricao"},
        2: {"title": "caminho", "sql_colname": "caminho"},
        3: {"title": "Abrir Arquivo"},
        4: {"title": "Abrir Diretório"},
    }

    def __init__(self, parent: QWidget, lancamento: ORMLancamentos):
        self.lancamento = lancamento
        self.table = self.get_table()
        self.import_file_line = self.get_import_file_line()
        self.tableline = AnexoTableLine(self)
        self.model_anexos = Anexos(lancamento.id)

        super(AnexosView, self).__init__(parent)

        self.setWindowTitle("Anexos")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout()
        layout.addLayout(self.import_file_line)
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.model_anexos.load()
        self.load_table_data()

    def get_table(self) -> QTableView:
        """
        Retorna tabela com o seu layout
        """
        table = QTableView()
        model = QStandardItemModel(0, len(self.COLUMNS))
        model.setHorizontalHeaderLabels([col["title"] for col in self.COLUMNS.values()])
        table.setModel(model)
        table.verticalHeader().setVisible(False)
        return table

    def get_import_file_line(self) -> QHBoxLayout:
        """
        Retorna toolbar
        """
        self.file_path = QLineEdit()
        self.file_path.setEnabled(False)

        layout = QHBoxLayout()
        layout.addWidget(QLabel("Importar arquivo:"))
        layout.addWidget(self.file_path)
        
        self.btn_procurar = QPushButton("Procurar...")
        self.btn_procurar.clicked.connect(self.on_procurar_clicked)
        layout.addWidget(self.btn_procurar)

        return layout

    def on_procurar_clicked(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        (file_name, selectedFilter) = dialog.getOpenFileName()
        if os.path.isfile(file_name):
            self.file_path.setText(file_name)
            self._on_importar_clicked(file_name)

    def _on_importar_clicked(self, file_name: str):
        data = self.lancamento.data

        dest_dir = Path.cwd() / "storage" / f"{data.year}" / f"{data.year}.{data.month:0>2}"
        dest_dir.mkdir(parents=True, exist_ok=True)

        shutil.copy(file_name, str(dest_dir))
        
        self.model_anexos.add_new(
            caminho=file_name,
            descricao=file_name,
            lancamento_id=self.lancamento.id
        )

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
                model.index(new_index, 2),
                {Qt.DisplayRole: row.caminho, Qt.UserRole: row.caminho},
            )

            self.table.setIndexWidget(
                model.index(new_index, 3),
                self.tableline.get_open_att_button(self, str(row.id)),
            )

            self.table.setIndexWidget(
                model.index(new_index, 4),
                self.tableline.get_open_att_dir_button(self, str(row.id)),
            )

        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(1)
        self.table.resizeColumnToContents(2)


    def on_open_att(self, index: QModelIndex):
        QMessageBox(text="Abrindo anexo.").exec()

    def on_open_att_dir(self, index: QModelIndex):
        QMessageBox(text="Abrindo dir anexo.").exec()


class AnexoTableLine(TableLine):
    def __init__(self, parent: AnexosView):
        super(AnexoTableLine, self).__init__()
        self.parent: AnexosView = parent

    @staticmethod
    def get_open_att_button(parent: AnexosView, index: QModelIndex):
        open_att_pbutt = QPushButton()
        open_att_pbutt.setToolTip("Abrir anexo")
        open_att_pbutt.setIcon(icons.abrir_anexo_arquivo())
        open_att_pbutt.clicked.connect(lambda: parent.on_open_att(index))
        return open_att_pbutt
    
    @staticmethod
    def get_open_att_dir_button(parent: AnexosView, index: QModelIndex):
        open_att_dir_pbutt = QPushButton()
        open_att_dir_pbutt.setToolTip("Abrir diretório do anexo")
        open_att_dir_pbutt.setIcon(icons.abrir_anexo_diretorio())
        open_att_dir_pbutt.clicked.connect(lambda: parent.on_open_att_dir(index))
        return open_att_dir_pbutt

