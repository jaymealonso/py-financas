import subprocess
import platform
import os.path
import shutil
from uuid import uuid4
from pathlib import Path
import view.icons.icons as icons
from view.TableLine import TableLine
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import Qt, pyqtSignal
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
    QMessageBox,
    QCheckBox,
)
from model import ORMLancamentos, ORMAnexos, Anexos
from util.settings import get_root_path


class AnexosView(QDialog):
    # anexo:ORMAnexos, total_anexos:int
    changed = pyqtSignal(ORMAnexos, int)

    COLUMNS = {
        0: {"title": "id", "sql_colname": "id"},
        1: {"title": "descricao", "sql_colname": "descricao"},
        2: {"title": "caminho", "sql_colname": "caminho"},
        3: {"title": "Nome Arquivo", "sql_colname": "nome_arquivo"},
        4: {"title": "Arquivo"},
        5: {"title": "Diretório"},
        6: {"title": "Remover"},
    }

    def __init__(self, parent: QWidget, lancamento: ORMLancamentos):
        self.lancamento = lancamento
        self.table = self.get_table()
        self.import_file_line = self.get_import_file_line()
        self.tableline = AnexoTableLine(self)
        self.model_anexos = Anexos(lancamento.id)

        super(AnexosView, self).__init__(parent)

        self.setWindowTitle(f"Anexos - (Lancamento {lancamento.id} | {lancamento.descricao})")
        self.setMinimumSize(1200, 600)
        self.resize(1600, 600)

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

    def _on_importar_clicked(self, file_fullpath: str):
        data = self.lancamento.data

        origin_file = Path(file_fullpath)
        dest_dir = Path(get_root_path(paths=["storage", f"{data.year}", f"{data.year}.{data.month:0>2}"]))
        uuid = uuid4()
        dest_file = dest_dir / f"{uuid}_{origin_file.name}"

        dest_dir.mkdir(parents=True, exist_ok=True)

        shutil.copy(file_fullpath, str(dest_file))

        anexo = self.model_anexos.add_new(
            id=str(uuid),
            descricao=origin_file.name,
            nome_arquivo=origin_file.name,
            lancamento_id=self.lancamento.id,
        )
        self.model_anexos.load()
        self.load_table_data()
        self.changed.emit(anexo, len(self.model_anexos.items))

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
                {
                    # Remove o diretorio base mantendo somente a estrutura dentro do
                    # diretorio em que o executavel (ou main.py) está contido
                    # ex: storage/2023/2023.03/file.txt
                    Qt.DisplayRole: str(Path(row.caminho)).replace(get_root_path(), ""),
                    Qt.UserRole: row.caminho,
                },
            )

            model.setItemData(
                model.index(new_index, 3),
                {Qt.DisplayRole: row.nome_arquivo, Qt.UserRole: row.nome_arquivo},
            )

            self.table.setIndexWidget(
                model.index(new_index, 4),
                self.tableline.get_open_att_button(self, row),
            )

            self.table.setIndexWidget(
                model.index(new_index, 5),
                self.tableline.get_open_att_dir_button(self, row),
            )

            self.table.setIndexWidget(
                model.index(new_index, 6),
                self.tableline.get_att_delete_button(self, row),
            )

        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 300)
        self.table.setColumnWidth(2, 300)
        self.table.setColumnWidth(3, 300)
        self.table.setColumnWidth(4, 150)
        self.table.setColumnWidth(5, 150)
        self.table.setColumnWidth(6, 150)

    def on_open_att(self, anexo_id: ORMAnexos.id):
        """Abre anexo"""
        anexo = self.model_anexos.by_id(anexo_id)
        if not anexo:
            return

        attach_path: str = anexo.caminho
        if platform.system() == "Darwin":  # macOS
            subprocess.call(("open", attach_path))
        elif platform.system() == "Windows":  # Windows
            os.startfile(attach_path)
        else:  # linux variants
            subprocess.call(("xdg-open", attach_path))

    def on_open_att_dir(self, anexo_id: ORMAnexos.id):
        """Abre diretório onde se localiza o anexo"""
        anexo = self.model_anexos.by_id(anexo_id)
        if not anexo:
            return

        attach_file: Path = Path(anexo.caminho)
        attach_path: str = str(attach_file.parents[0])
        if platform.system() == "Darwin":  # macOS
            subprocess.call(("open", attach_path))
        elif platform.system() == "Windows":  # Windows
            os.startfile(attach_path)
        else:  # linux variants
            subprocess.call(("xdg-open", attach_path))

    def on_del_att(self, anexo_id: ORMAnexos.id):
        """Apaga anexo"""
        anexo = self.model_anexos.by_id(anexo_id)
        if not anexo:
            return

        question = QMessageBox(
            QMessageBox.Icon.Question,
            "Remove Anexo?",
            f'Deseja remover o anexo "{anexo.nome_arquivo}" ?',
            parent=self,
            buttons=QMessageBox.Yes | QMessageBox.No,
        )
        self.checkbox = QCheckBox("Eliminar arquivo físico?")
        self.checkbox.setEnabled(anexo.caminho.strip() != "")
        self.checkbox.setChecked(anexo.caminho.strip() != "")
        question.setCheckBox(self.checkbox)
        question.setDefaultButton(QMessageBox.No)
        button = question.exec()
        if button == QMessageBox.No:
            return

        self.model_anexos.delete(anexo.id, delete_file=self.checkbox.isChecked())
        self.model_anexos.load()
        self.load_table_data()
        self.changed.emit(anexo, len(self.model_anexos.items))


class AnexoTableLine(TableLine):
    def __init__(self, parent: AnexosView):
        super(AnexoTableLine, self).__init__()
        self.parent: AnexosView = parent

    @staticmethod
    def get_open_att_button(parent: AnexosView, anexo: ORMAnexos):
        open_att_pbutt = QPushButton()
        open_att_pbutt.setToolTip("Abrir anexo")
        open_att_pbutt.setIcon(icons.abrir_anexo_arquivo())
        open_att_pbutt.setEnabled(anexo.caminho.strip() != "")
        open_att_pbutt.clicked.connect(lambda: parent.on_open_att(anexo.id))
        return open_att_pbutt

    @staticmethod
    def get_open_att_dir_button(parent: AnexosView, anexo: ORMAnexos):
        open_att_dir_pbutt = QPushButton()
        open_att_dir_pbutt.setToolTip("Abrir diretório do anexo")
        open_att_dir_pbutt.setIcon(icons.abrir_anexo_diretorio())
        open_att_dir_pbutt.setEnabled(anexo.caminho.strip() != "")
        open_att_dir_pbutt.clicked.connect(lambda: parent.on_open_att_dir(anexo.id))
        return open_att_dir_pbutt

    @staticmethod
    def get_att_delete_button(parent: AnexosView, anexo: ORMAnexos):
        del_pbutt = QPushButton()
        del_pbutt.setToolTip("Eliminar Anexo")
        del_pbutt.setIcon(icons.delete())
        # deixa enable caso o caminho esteja invalido mas ainda pode deletar o
        # registro da base de dados
        # del_pbutt.setEnabled(anexo.caminho.strip() != "")
        del_pbutt.clicked.connect(lambda: parent.on_del_att(anexo.id))
        return del_pbutt
