import sys
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
    MAIN = "Janela-Contas"
    CONTA_LANC = "Conta-Lancamento"


class Settings:
    def __init__(self):
        super(Settings, self).__init__()
        
        self.settings = QSettings(get_root_path("config.ini"), QSettings.IniFormat)   

    @property
    def db_location(self) -> str:
        DATABASE_DEFAULT_FILENAME = "database.db"
        try:
            default_path = get_root_path(DATABASE_DEFAULT_FILENAME) # Path.cwd() / DATABASE_DEFAULT_FILENAME
            path = self.settings.value(f"{ConfigGroups.PADROES.value}/db_path")
            if not path:
                self.db_location = str(default_path)
                path = default_path
            return path
        except Exception as e:
            logging.error(f"Error loading DB path {e}.")
            return None

    @db_location.setter
    def db_location(self, path: str):
        self.settings.beginGroup(ConfigGroups.PADROES.value)
        self.settings.setValue(f"db_path", path)
        self.settings.endGroup()

    def save_main_w_settings(self, window: QWidget):
        self.settings.beginGroup(ConfigGroups.MAIN.value)
        self.settings.setValue(f"geometry", window.saveGeometry())
        self.settings.endGroup()

    def load_main_w_settings(self, window: QWidget):
        try:
            geometry = self.settings.value(f"{ConfigGroups.MAIN.value}/geometry")
            window.restoreGeometry(geometry)
            return True
        except Exception as e:
            logging.error(f"Error loading window settings {e}.")
            return False

    def save_lanc_settings(self, window: QWidget, conta_id: int):
        """Salvar configuracoes de posicao nas janelas de lançamento"""
        self.settings.beginGroup(f"{ConfigGroups.CONTA_LANC.value}-{conta_id}")
        self.settings.setValue(f"geometry", window.saveGeometry())
        self.settings.endGroup()

    def load_lanc_settings(self, window: QWidget, conta_id: int):
        """Carregar configuracoes de posicao nas janelas de lançamento"""
        try:
            geometry = self.settings.value(f"{ConfigGroups.CONTA_LANC.value}-{conta_id}/geometry")
            # wState = self.settings.value(f"lanc-{conta_dc.id}-windowState")

            window.restoreGeometry(geometry)
            # window.setWindowState(wState)
            return True
        except Exception as e:
            logging.error(f"Error loading window settings {e}.")
            return False

def get_root_path(filename: str = "", paths: list[str] = []) -> str:
    """
    Busca raiz onde o executavel se localiza no BUNDLED, ou caminho base na execução no não BUNDLE(main.py)
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        logging.info('Executando em um Bundle PyInstaller.')
        # return Path(__file__).resolve().with_name(filename)
        # logging.info(f'sys._MEIPASS: "{sys._MEIPASS}".')
        # logging.info(f'sys.executable: "{sys.executable}".')
        path = Path(sys.executable).resolve()
        if len(paths) > 0:
            path = path.joinpath(paths)
        path.with_name(filename)
        logging.info(f'Retornando caminho: "{path}".')
        return str(path)
        # return sys._MEIPASS
    else:
        logging.info('Executando em um processo Python normal. Não Bundled.') 
        # vai dois niveis para baixo, assume-se que este arquivo(settings.py) está no diretório 
        #   "./py-financas/src/util/settings.py"
        # mas deve-se retornar
        #   "./py-financas/{filename}"
        path = Path(__file__).parents[2]
        if len(paths) > 0:
            path = path.joinpath(*paths)
        path = path / filename
        logging.info(f'Retornando caminho: "{path}".')
        return str(path)
        # return Path.cwd() / filename




