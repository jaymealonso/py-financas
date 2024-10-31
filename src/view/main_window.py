from lib.Genericos.log import logging
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QTabWidget,
    QApplication,
    QSizePolicy,
)
from lib import CustomToolbar
from util.toaster import QToaster
from view.configuracao_vw import ConfiguracaoView
from view.contas_vw import ContasView
from view.agenda_vw import AgendaView
from view.categorias_vw import CategoriasView
import view.icons.icons as icons
from util.settings import Settings


class MainWindow(QMainWindow):
    def __init__(self, app: QApplication):
        super(MainWindow, self).__init__()

        self.app = app
        self.global_settings = Settings()
        self.settings = self.global_settings.janela_contas
        self.tabbar = self.get_tabbar()
        self.toolbar = self.addToolBar("Main")
        self.fill_toolbar(self.toolbar)

        self.setWindowTitle("Finanças - Python")
        self.setMinimumSize(800, 600)
        try:
            self.restoreGeometry(self.settings.dimensoes)
        except Exception as e:
            logging.info(f"Sem tamanho padrão da janela.{e}")
            self.resize(1600, 900)

        layout = QVBoxLayout(self.window())
        layout.addWidget(self.tabbar)
        self.container = QWidget(self)
        self.container.setLayout(layout)

        self.setCentralWidget(self.container)

    def closeEvent(self, event) -> None:
        print("Entrou evento close")
        self.app.closeAllWindows()

        self.settings.dimensoes = self.saveGeometry()

        # @todo: descomentar antes de liberar
        # result = QMessageBox.question(self, "Sair?", "Deseja fechar o aplicativo?", QMessageBox.Yes | QMessageBox.No)
        # event.ignore()
        # if result == QMessageBox.Yes:
        #     self.app.closeAllWindows()
        #     event.accept()

    def get_tabbar(self):
        self.tabbar = QTabWidget(self.window())

        self.tabbar.addTab(ContasView(self), "Contas")
        self.tabbar.addTab(CategoriasView(), "Categorias")
        # self.tabbar.addTab(AgendaView(), "Agenda")

        return self.tabbar

    def fill_toolbar(self, toolbar: CustomToolbar):
        # oculta menu popup que deixa ocultar a toolbar
        toolbar.toggleViewAction().setVisible(False)
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(64, 64))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer)

        config_act = toolbar.addAction(icons.configurar(), "Configurar")
        config_act.triggered.connect(self.on_configure)

    def on_undo(self):
        QToaster.showMessage(self, "On UNDO clicked")
        pass

    def on_redo(self):
        QToaster.showMessage(self, "On REDO clicked")
        pass

    def on_configure(self):
        config_vw = ConfiguracaoView(self)
        config_vw.show()

    def on_load(self, s):
        QToaster.showMessage(self, "On LOAD clicked")

    def on_save(self):
        QToaster.showMessage(self, "On SAVE clicked")
