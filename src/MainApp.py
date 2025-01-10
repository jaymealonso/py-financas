import sys
from contextlib import suppress

import view.icons.icons as icons
from view.contas_vw import ContasView
from util.settings import Settings
from pathlib import Path
from argparse import ArgumentParser
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt5.QtCore import QFile, QTextStream, QDir, Qt
from view.main_window import MainWindow
from model import Database


class MainApp:
    def __init__(self):
        self.app = self.create_app()

    def startup(self):
        self.settings = Settings()
        self.arg_parser: ArgumentParser = self.configure_arguments_parser()
        self.args = self.arg_parser.parse_args()
        self.db: Database = None
        self.setup_theme(self.args.theme)
        self.db = self.prepare_database(drop=self.args.drop, populate_sample=self.args.sample)

    def prepare_database(self, drop: bool = False, populate_sample: bool = False) -> Database:
        db = Database()
        if not db.exists():
            QMessageBox.critical(
                None, "Erro ao abrir base de dados", "Arquivo escolhido como base de dados não é compativel."
            )
            sys.exit(1)
        if drop:
            db.drop_all()
        db.run_initial_load(populate_sample)
        return db

    def configure_arguments_parser(self) -> ArgumentParser:
        """
        Configura argumentos de linha de comando
        """
        parser = ArgumentParser(description="Programa de finanças")
        parser.add_argument("-D", "--drop", help="Elimina dados da base de dados.", action="store_true")
        parser.add_argument(
            "-s",
            "--sample",
            help="Adiciona dados de exemplo na base de dados.",
            action="store_true",
        )
        parser.add_argument(
            "-o",
            "--conta",
            dest="conta_id",
            type=int,
            help="Ao iniciar abre a conta com o ID indicado, se ela existir.",
        )
        parser.add_argument(
            "-T",
            "--theme",
            dest="theme",
            help="Nome do diretório do tema dentro de ./themes/<THEME>.",
            type=str,
        )

        return parser

    def create_app(self) -> QApplication:
        new_app = QApplication([])
        new_app.setStyle("Fusion")
        new_app.setWindowIcon(icons.app_icon())
        return new_app

    def show(self):
        self.window = MainWindow(self.app)
        self.window.show()
        if self.args.conta_id:
            contas_vw: ContasView = self.window.tabbar.widget(0)
            conta_indexes = contas_vw.table.model().findItems(
                str(self.args.conta_id), Qt.MatchExactly, contas_vw.Column.ID
            )
            if conta_indexes:
                conta_index = conta_indexes[0]
                contas_vw.on_open_lancamentos(conta_index)

    def setup_theme(self, theme_name: str):
        if theme_name is None:
            theme_name = self.settings.theme
        path = Path.cwd() / "themes" / theme_name
        QDir.addSearchPath(theme_name, str(path))

        file = QFile(f"{theme_name}:stylesheet.qss")
        file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(file)
        self.app.setStyleSheet(stream.readAll())


# class SplashWindow:
#     def __init__(self):
#         path = os.path.dirname(os.path.abspath(__file__))
#         splash_pix = QtGui.QPixmap(f"{path}/imagens/splash.png")
#         self.splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
#
#     def show(self) -> QSplashScreen:
#         self.splash.show()
#
#     def close(self):
#         self.splash.close()  # close the splash scre


class SplashWindow:
    def show(self) -> QSplashScreen:
        pass
        # if getattr(sys, 'frozen', False):
        #     with suppress(ModuleNotFoundError):
        #         import pyi_splash  # noqa
        #         pyi_splash.close()

    def close(self):
        if getattr(sys, "frozen", False):
            with suppress(ModuleNotFoundError):
                import pyi_splash  # noqa

                pyi_splash.close()
