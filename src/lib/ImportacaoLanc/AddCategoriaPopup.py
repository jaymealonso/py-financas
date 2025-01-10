#!

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QCheckBox,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
import view.icons.icons as icons
from lib import CustomToolbar
from model import Categorias, ORMCategorias


class AddCategoriasPopup(QDialog):
    categ_created = pyqtSignal()

    def __init__(self, parent: QWidget, new_categorias: list[str]) -> None:
        super().__init__(parent)

        # QDialog props
        self.setWindowTitle("Criar categorias")
        self.setMinimumSize(150, 150)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        # local vars
        self.new_categorias = new_categorias
        self.checkboxes = list[QCheckBox]
        self.model_categoria = Categorias()

        # layout
        layout = QVBoxLayout()
        layout.addWidget(self.get_toolbar())
        layout.addWidget(self.get_checkbox_list())
        layout.addWidget(self.get_actionbar())

        self.setLayout(layout)

    def get_toolbar(self) -> CustomToolbar:
        toolbar = CustomToolbar()
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        btn_sele_all = toolbar.addAction(icons.select_all(), "Marca todos")
        btn_sele_all.triggered.connect(self.on_marca_todos)

        btn_dsel_all = toolbar.addAction(icons.deselect_all(), "Desmarca todos")
        btn_dsel_all.triggered.connect(self.on_desmarca_todos)

        return toolbar

    def on_marca_todos(self):
        check: QCheckBox = None
        for check in self.checkboxes:
            check.setChecked(True)

    def on_desmarca_todos(self):
        check: QCheckBox = None
        for check in self.checkboxes:
            check.setChecked(False)

    def get_checkbox_list(self):
        scroll_area = QScrollArea()
        container = QWidget()
        grid = QGridLayout()

        self.checkboxes = []
        for index, categoria in enumerate(self.new_categorias):
            check = QCheckBox(categoria)
            self.checkboxes.append(check)
            grid.addWidget(check, index, 0)

        container.setLayout(grid)

        scroll_area.setWidget(container)
        return scroll_area

    def get_actionbar(self) -> QWidget:
        actionbar = QWidget()
        actionbar.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        btn_criar = QPushButton("Criar")
        btn_criar.clicked.connect(self.on_criar)
        btn_fechar = QPushButton("Fechar")
        btn_fechar.clicked.connect(self.close)
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(btn_criar)
        hbox.addWidget(btn_fechar)
        actionbar.setLayout(hbox)
        return actionbar

    def on_criar(self):
        check: QCheckBox = None
        created_count = 0
        for check in self.checkboxes:
            if check.isChecked():
                self.model_categoria.add_new(ORMCategorias(id=None, nm_categoria=check.text().strip()))
                created_count += 1

        if created_count > 0:
            QMessageBox.information(self, "Sucesso", f"{ created_count } categorias criadas.")
            self.categ_created.emit()
            self.close()
