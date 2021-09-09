import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from util.toaster import QToaster
from view.lanc_table import LancamentosTab
from view.contas_table import ContasTab
from view.agenda_tab import AgendaTab


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Finanças - Python")
        self.setMinimumSize(800, 600)
        self.resize(1600, 900)

        self.tabbar = self.get_tabbar()
        self.toolbar = self.addToolBar("Main")
        self.fill_toolbar(self.toolbar)

        layout = QVBoxLayout()
        layout.addWidget(self.tabbar)
        self.container = QWidget()
        self.container.setLayout(layout)

        self.setCentralWidget(self.container)

    def get_tabbar(self):
        self.tabbar = QTabWidget()

        self.tabbar.addTab(ContasTab(), "Contas")
        self.tabbar.addTab(LancamentosTab(), "Lançamentos")
        self.tabbar.addTab(AgendaTab(), "Agenda")

        return self.tabbar

    def fill_toolbar(self, toolbar: QToolBar):
        # oculta menu popup que deixa ocultar a toolbar
        toolbar.toggleViewAction().setVisible(False)
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(64, 64))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        path = os.path.dirname(os.path.abspath(__file__))
        save_act = toolbar.addAction(
            QIcon(QPixmap(path + r".\icons\open_folder.png")),
            "Load"
        )
        save_act.triggered.connect(self.on_load)

        load_act = toolbar.addAction(
            QIcon(QPixmap(path + r".\icons\save_as.png")),
            "Save"
        )
        load_act.triggered.connect(self.on_save)

        load_act = toolbar.addAction(
            QIcon(QPixmap(path + r".\icons\add.png")),
            "Add"
        )
        load_act.triggered.connect(self.on_add)

        load_act = toolbar.addAction(
            QIcon(QPixmap(path + r".\icons\delete.png")),
            "Remove"
        )
        load_act.triggered.connect(self.on_remove)

    def on_load(self, s):
        QToaster.showMessage(self, "On LOAD clicked", closable=False, timeout=2000, corner=Qt.BottomRightCorner)

    def on_save(self):
        QToaster.showMessage(self, "On SAVE clicked", closable=False, timeout=2000, corner=Qt.BottomRightCorner)

    def on_add(self):
        new_margin = [i+1 for i in self.container.getContentsMargins()]
        print(f'new margins {new_margin}')
        self.container.setContentsMargins(*new_margin)

        QToaster.showMessage(self, "On ADD clicked", closable=False, timeout=2000, corner=Qt.BottomRightCorner)

    def on_remove(self):
        new_margin = [i-1 for i in self.container.getContentsMargins()]
        print(f'new margins {new_margin}')
        self.container.setContentsMargins(*new_margin)

        QToaster.showMessage(self, "On REMOVE clicked", closable=False, timeout=2000, corner=Qt.BottomRightCorner)
