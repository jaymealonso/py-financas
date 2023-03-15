import logging
from pathlib import Path
from enum import Enum
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QWidget

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


class ConfigGroups(Enum):
    PADROES = "Padroes"
    MAIN = "MainWindow"
    CONTA_LANC = "Conta-Lancamento"

class Settings:
    def __init__(self):
        super(Settings, self).__init__()
        
        self.settings = QSettings("config.ini", QSettings.IniFormat)   
        # self.settings = QSettings(
        #     QSettings.IniFormat, QSettings.UserScope, "JALL Soft", "Finanças Py"
        # )

    @property
    def db_location(self) -> str:
        DATABASE_FILENAME = "database.db"
        try:
            default_path = Path.cwd() / DATABASE_FILENAME
            path = self.settings.value(f"{ConfigGroups.PADROES.name}/db_path")
            if not path:
                self.db_location = str(default_path)
                path = default_path
            return path
        except Exception as e:
            logging.error(f"Error loading DB path {e}.")
            return None

    @db_location.setter
    def db_location(self, path: str):
        self.settings.beginGroup(ConfigGroups.PADROES.name)
        self.settings.setValue(f"db_path", path)
        self.settings.endGroup()

    def save_main_w_settings(self, window: QWidget):
        self.settings.beginGroup(ConfigGroups.MAIN.name)
        self.settings.setValue(f"geometry", window.saveGeometry())
        self.settings.endGroup()

    def load_main_w_settings(self, window: QWidget):
        try:
            geometry = self.settings.value(f"{ConfigGroups.MAIN.name}/geometry")
            window.restoreGeometry(geometry)
            return True
        except Exception as e:
            logging.error(f"Error loading window settings {e}.")
            return False

    def save_lanc_settings(self, window: QWidget, conta_id: int):
        """Salvar configuracoes de posicao nas janelas de lançamento"""
        self.settings.beginGroup(f"{ConfigGroups.CONTA_LANC.name}-{conta_id}")
        self.settings.setValue(f"geometry", window.saveGeometry())
        self.settings.endGroup()

    def load_lanc_settings(self, window: QWidget, conta_id: int):
        """Carregar configuracoes de posicao nas janelas de lançamento"""
        try:
            geometry = self.settings.value(f"{ConfigGroups.CONTA_LANC.name}-{conta_id}/geometry")
            # wState = self.settings.value(f"lanc-{conta_dc.id}-windowState")

            window.restoreGeometry(geometry)
            # window.setWindowState(wState)
            return True
        except Exception as e:
            logging.error(f"Error loading window settings {e}.")
            return False
    