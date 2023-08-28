import sys
import view.icons.icons as icons
from util.settings import Settings
from pathlib import Path
from argparse import ArgumentParser
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QFile, QTextStream, QDir, QCoreApplication
from view.main_window import MainWindow
from model.db.db import Database


class MainApp:
    def __init__(self):
        self.settings = Settings()
        self.arg_parser: ArgumentParser = self.configure_arguments_parser()
        self.args = self.arg_parser.parse_args()
        self.app = self.create_app()
        self.db: Database = None
        self.setup_theme(self.args.theme)

    def startup(self):
        self.db = self.prepare_database(
            drop=self.args.drop, populate_sample=self.args.sample
        )

    def prepare_database(
        self, drop: bool = False, populate_sample: bool = False
    ) -> Database:
        db = Database()
        if not db.exists():
            QMessageBox.critical(None, 'Erro ao abrir base de dados',
                'Arquivo escolhido como base de dados não é compativel.')
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
        parser.add_argument(
            "-D", "--drop", help="Elimina dados da base de dados.", action="store_true"
        )
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
            self.window.tabbar.widget(0).on_open_lancamentos(self.args.conta_id)

    def setup_theme(self, theme_name: str):
        if theme_name is None:
            theme_name = self.settings.theme
        path = Path.cwd() / "themes" / theme_name
        QDir.addSearchPath(theme_name, str(path))

        file = QFile(f"{theme_name}:stylesheet.qss")
        file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(file)
        self.app.setStyleSheet(stream.readAll())


if __name__ == "__main__":
    app = MainApp()
    app.startup()
    app.show()

    sys.exit(app.app.exec_())
