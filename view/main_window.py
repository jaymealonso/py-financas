from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTabWidget, QToolBar, QApplication, QSizePolicy
from util.toaster import QToaster
from view.contas_vw import ContasView
from view.agenda_vw import AgendaView
from view.categorias_vw import CategoriasView
import view.icons.icons as icons


class MainWindow(QMainWindow):
    def __init__(self, app:QApplication):
        super(MainWindow, self).__init__()

        self.app = app
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

    def closeEvent(self, event) -> None:
        print("Entrou evento close")
        self.app.closeAllWindows()
        # @todo: descomentar antes de liberar
        # result = QMessageBox.question(self, "Sair?", "Deseja fechar o aplicativo?", QMessageBox.Yes | QMessageBox.No)
        # event.ignore()
        # if result == QMessageBox.Yes:
        #     self.app.closeAllWindows()
        #     event.accept()

    def get_tabbar(self):
        self.tabbar = QTabWidget()

        self.tabbar.addTab(ContasView(self), "Contas")
        # self.tabbar.addTab(LancamentosTab(), "Lançamentos")
        self.tabbar.addTab(CategoriasView(), "Categorias")
        self.tabbar.addTab(AgendaView(), "Agenda")

        return self.tabbar

    def fill_toolbar(self, toolbar: QToolBar):
        # oculta menu popup que deixa ocultar a toolbar
        toolbar.toggleViewAction().setVisible(False)
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(64, 64))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        save_act = toolbar.addAction(
            icons.load(), "Carregar"
        )
        save_act.triggered.connect(self.on_load)

        load_act = toolbar.addAction(
            icons.save(), "Salvar"
        )
        load_act.triggered.connect(self.on_save)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer)

        config_act = toolbar.addAction(
            icons.configurar(), "Configurar"
        )
        config_act.triggered.connect(self.on_configure)

    def on_configure(self):
        QToaster.showMessage(self, "On CONFIGURAR clicked", closable=False, timeout=2000, corner=Qt.BottomRightCorner)

    def on_load(self, s):
        QToaster.showMessage(self, "On LOAD clicked", closable=False, timeout=2000, corner=Qt.BottomRightCorner)

    def on_save(self):
        QToaster.showMessage(self, "On SAVE clicked", closable=False, timeout=2000, corner=Qt.BottomRightCorner)
