from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from util.toaster import QToaster
from lanc_table import LancamentosTable


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Finanças - Python")
        self.setMinimumSize(800, 600)

        tb = self.addToolBar("Main")
        self.fill_toolbar(tb)
        self.setCentralWidget(self.get_tabbar())

    def get_tabbar(self):
        tabbar = QTabWidget()
        tabbar.setSizeIncrement(10,10)
        tabbar.addTab(self.__get_table(), "Contas")

        return tabbar

    def fill_toolbar(self, toolbar: QToolBar):
        # oculta menu popup que deixa ocultar a toolbar
        toolbar.toggleViewAction().setVisible(False)
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(64, 64))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        save_act = toolbar.addAction(
            QIcon(QPixmap(r"C:\Users\Jayme\Downloads\py-financas\view\icons\Folder-Open.png")),
            "Load"
        )
        save_act.triggered.connect(self.on_load)

        load_act = toolbar.addAction(
            QIcon(QPixmap(r"C:\Users\Jayme\Downloads\py-financas\view\icons\Save.png")),
            "Save"
        )
        load_act.triggered.connect(self.on_save)

    def on_load(self, s):
        QToaster.showMessage(self, "On LOAD clicked", closable=False, timeout=2000, corner=Qt.BottomRightCorner)

    def on_save(self):
        QToaster.showMessage(self, "On SAVE clicked", closable=False, timeout=2000, corner=Qt.BottomRightCorner)

    def __get_table(self):
        table = LancamentosTable()  # QTableWidget(0, 4)

        return table
