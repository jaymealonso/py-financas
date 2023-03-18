import subprocess
import platform
import os.path
import shutil
from pathlib import Path
import view.icons.icons as icons
from view.TableLine import TableLine
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import (
    QWidget,
    QTableView,
    QVBoxLayout,
    QDialog,
    QPushButton,
    QLineEdit,
    QHBoxLayout,
    QLabel,
    QFileDialog,
)
from model.db.db_orm import Lancamentos as ORMLancamentos
from model.Anexos import Anexos


class AnexosView(QDialog):
    COLUMNS = {
        0: {"title": "id", "sql_colname": "id"},
        1: {"title": "descricao", "sql_colname": "descricao"},
        2: {"title": "caminho", "sql_colname": "caminho"},
        3: {"title": "Arquivo"},
        4: {"title": "Diretório"},
        5: {"title": "Remover"},
    }

    def __init__(self, parent: QWidget, lancamento: ORMLancamentos):
        self.lancamento = lancamento
        self.table = self.get_table()
        self.import_file_line = self.get_import_file_line()
        self.tableline = AnexoTableLine(self)
        self.model_anexos = Anexos(lancamento.id)

        super(AnexosView, self).__init__(parent)

        self.setWindowTitle(
            f"Anexos - (Lancamento {lancamento.id} | {lancamento.descricao})"
        )
        self.setMinimumSize(1200, 600)

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
        self.btn_procurar.clicked.connect(self.on_armazenar_arq_clicked)
        layout.addWidget(self.btn_procurar)

        return layout

    def on_armazenar_arq_clicked(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        (file_name, selectedFilter) = dialog.getOpenFileName()
        if os.path.isfile(file_name):
            self.file_path.setText(file_name)
            self._on_importar_clicked(file_name)

    def _on_importar_clicked(self, file_name: str):
        data = self.lancamento.data

        origin_file = Path(file_name)
        dest_dir = (
            Path.cwd() / "storage" / f"{data.year}" / f"{data.year}.{data.month:0>2}"
        )
        dest_dir.mkdir(parents=True, exist_ok=True)

        shutil.copy(file_name, str(dest_dir))

        self.model_anexos.add_new(
            caminho=f"{str(dest_dir)}/{origin_file.name}",
            descricao=origin_file.name,
            lancamento_id=self.lancamento.id,
        )
        self.load_table_data()

    def load_table_data(self) -> None:
        """
        Popula tabela com os dados do modelo, redimensiona colunas
        """
        model = self.table.model()

        # clear table
        model.setRowCount(0)

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
                self.tableline.get_open_att_button(self, row.id),
            )

            self.table.setIndexWidget(
                model.index(new_index, 4),
                self.tableline.get_open_att_dir_button(self, row.id),
            )

            self.table.setIndexWidget(
                model.index(new_index, 5),
                self.tableline.get_att_delete_button(self, row.id),
            )

        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(1)
        self.table.resizeColumnToContents(2)

    def on_open_att(self, index: int):
        attachments = [item for item in self.model_anexos.items if item.id == index]
        if len(attachments) != 1:
            return

        attach_path: str = attachments[0].caminho
        if platform.system() == "Darwin":  # macOS
            subprocess.call(("open", attach_path))
        elif platform.system() == "Windows":  # Windows
            os.startfile(attach_path)
        else:  # linux variants
            subprocess.call(("xdg-open", attach_path))

    def on_open_att_dir(self, index: QModelIndex):
        attachments = [item for item in self.model_anexos.items if item.id == index]
        if len(attachments) != 1:
            return

        attach_file: Path = Path(attachments[0].caminho)
        attach_path: str = str(attach_file.parents[0])
        if platform.system() == "Darwin":  # macOS
            subprocess.call(("open", attach_path))
        elif platform.system() == "Windows":  # Windows
            os.startfile(attach_path)
        else:  # linux variants
            subprocess.call(("xdg-open", attach_path))

    def on_del_att(self, index: QModelIndex):
        ...


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

    @staticmethod
    def get_att_delete_button(parent: AnexosView, index: QModelIndex):
        del_pbutt = QPushButton()
        del_pbutt.setToolTip("Eliminar Anexo")
        del_pbutt.setIcon(icons.delete())
        del_pbutt.clicked.connect(lambda: parent.on_del_att(index))
        return del_pbutt
