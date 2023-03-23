import sys
import logging
import darkdetect
from pathlib import Path
from enum import Enum
from PyQt5.QtCore import QSettings, QRect
from PyQt5.QtWidgets import QWidget, QApplication
from abc import ABC
from util.singleton_meta import SingletonMeta

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


class JanelaSettings(ABC):
    def __init__(self, settings: QSettings, group:str):
        super(JanelaSettings, self).__init__()
        self.group = group
        self.settings = settings

    @property
    def dimensoes(self) -> QRect:
        # try:
        geometry = self.settings.value(f"{self.group}/geometry")
        if geometry is None:
            raise Exception(f"Geometria da janela {self.group} tá vazia") 
        return geometry
    
    @dimensoes.setter
    def dimensoes(self, geometry: QRect): 
        self.settings.beginGroup(self.group)
        self.settings.setValue(f"geometry", geometry)
        self.settings.endGroup()


class JanelaContasSettings(JanelaSettings):
    def __init__(self, settings: QSettings):
        super(JanelaContasSettings, self).__init__(
            settings, 
            group="Janela-Contas"
        )

class JanelaLancamentosSettings(JanelaSettings):
    def __init__(self, settings: QSettings, conta_id: str):
        super(JanelaLancamentosSettings, self).__init__(
            settings, 
            group=f"Conta-Lancamento-{conta_id}"
        )
        self.conta_id = conta_id

class Settings(metaclass=SingletonMeta):
    PADROES = "Padroes"
    def __init__(self):
        super(Settings, self).__init__()

        self.settings = QSettings(get_root_path("config.ini"), QSettings.IniFormat)   

        self.janela_contas = JanelaContasSettings(self.settings)
        self.janelas_lancamentos: list[JanelaLancamentosSettings] = []

    @property
    def db_location(self) -> str:
        DATABASE_DEFAULT_FILENAME = "database.db"
        try:
            path = self.settings.value(f"{Settings.PADROES}/db_path")
            if not path:
                default_path = get_root_path(DATABASE_DEFAULT_FILENAME)
                self.db_location = str(default_path)
                path = default_path
            return path
        except Exception as e:
            logging.error(f"Error loading DB path {e}.")
            return None

    @db_location.setter
    def db_location(self, path: str):
        self.settings.beginGroup(Settings.PADROES)
        self.settings.setValue(f"db_path", path)
        self.settings.endGroup()

    @property
    def theme(self) -> str:
        theme_name = self.settings.value(f"{Settings.PADROES}/theme")
        if theme_name == "" or theme_name is None:
            theme_name = "light" if darkdetect.isLight() else "dark"
            self.theme = theme_name
        return theme_name

    @theme.setter
    def theme(self, theme_name: str):
        self.settings.beginGroup(Settings.PADROES)
        self.settings.setValue(f"theme", theme_name)
        self.settings.endGroup()

    def load_lanc_settings(self, conta_id: int) -> JanelaLancamentosSettings:

        janela_array = [janela for janela in self.janelas_lancamentos if janela.conta_id == conta_id]
        if len(janela_array) != 0:
            janela = janela_array[0]
        else:
            janela = JanelaLancamentosSettings(self.settings, conta_id)
            self.janelas_lancamentos.append(janela)
        
        return janela

def get_root_path(filename: str = "", paths: list[str] = []) -> str:
    """
    Busca raiz onde o executavel se localiza no BUNDLED, ou caminho base na execução no não BUNDLE(main.py)
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        logging.info('Executando em um Bundle PyInstaller.')
        path = Path(sys.executable).parents[0]
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


