import sys
import view.icons.icons as icons
from argparse import ArgumentParser
from PyQt5.QtWidgets import QApplication
from view.main_window import MainWindow
from model.db.db import Database


class MainApp:
    def __init__(self):
        self.arg_parser:ArgumentParser = self.configure_arguments_parser()
        self.args = self.arg_parser.parse_args()

        self.db = self.prepare_database(drop=self.args.drop, populate_sample=self.args.sample)
        self.app = self.create_app()

    def prepare_database(self, drop: bool=False, populate_sample:bool=False) -> Database:
        db = Database()
        if drop:
            db.drop_all()
        db.run_initial_load(populate_sample)
        return db

    def configure_arguments_parser(self) -> ArgumentParser:
        """
        Configura argumentos de linha de comando
        """
        parser = ArgumentParser(description="Programa de finanças")
        parser.add_argument("-D", "--drop", help="Elimina dados da base de dados.", action='store_true')
        parser.add_argument("-s", "--sample", help="Adiciona dados de exemplo na base de dados.", action='store_true')
        parser.add_argument("-o", "--conta", dest="conta_id", type=int, \
            help="Ao iniciar abre a conta com o ID indicado, se ela existir.")
        return parser
        
    def create_app(self) -> QApplication:
        app = QApplication([])
        app.setStyle("Fusion")
        app.setWindowIcon(icons.app_icon())
        return app

    def show(self):
        self.window = MainWindow(self.app)
        self.window.show()
        if self.args.conta_id:
            self.window.tabbar.widget(0).on_open_lancamentos(self.args.conta_id)


if __name__ == "__main__":
    app = MainApp()
    app.show()

    sys.exit(app.app.exec_())
