from model.Conta import Conta
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QWidget


class Settings:
    def __init__(self):
        super(Settings, self).__init__()
        self.settings = QSettings(
            QSettings.IniFormat, QSettings.UserScope,
            "JALL Soft", "Finanças Py")

    def save_main_w_settings(self, window: QWidget):
        self.settings.setValue(
            f"mainWindow/geometry",
            window.saveGeometry())

    def load_main_w_settings(self, window: QWidget):
        try:
            geometry = self.settings.value(f"mainWindow/geometry")
            window.restoreGeometry(geometry)
            return True
        except Exception as e:
            print(f"Error loading window settings {e}.")
            return False

    def save_lanc_settings(self, window: QWidget, conta_dc: Conta):
        """ Salvar configuracoes de posicao nas janelas de lançamento """
        self.settings.setValue(
            f"lanc-{conta_dc.id}/geometry",
            window.saveGeometry())
        # self.settings.setValue(
        #     f"lanc-{conta_dc.id}-windowState",
        #     window.saveState()
        # )

    def load_lanc_settings(self, window: QWidget, conta_dc:Conta):
        """ Carregar configuracoes de posicao nas janelas de lançamento """
        try:
            geometry = self.settings.value(f"lanc-{conta_dc.id}/geometry")
            # wState = self.settings.value(f"lanc-{conta_dc.id}-windowState")

            window.restoreGeometry(geometry)
            # window.setWindowState(wState)
            return True
        except Exception as e:
            print(f"Error loading window settings {e}.")
            return False


