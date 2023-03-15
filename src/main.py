import sys
import view.icons.icons as icons
from argparse import ArgumentParser
from PyQt5.QtWidgets import QApplication
from view.main_window import MainWindow
from model.db.db import Database


class MainApp:
    def __init__(self, drop_tables: bool, populate_sample: bool, open_conta_id: int=None):
        self.app = QApplication([])
        self.app.setStyle("Fusion")

        self.app.setWindowIcon(icons.app_icon())

        self.db = Database()
        if drop_tables:
            self.db.drop_all()
        self.db.run_initial_load(populate_sample)
        self.window = MainWindow(self.app, open_conta_id)
        self.window.show()


if __name__ == "__main__":
    parser = ArgumentParser(description="Programa de finanças")
    parser.add_argument("-D", "--drop", help="Elimina dados da base de dados.", action='store_true')
    parser.add_argument("-s", "--sample", help="Adiciona dados de exemplo na base de dados.", action='store_true')
    parser.add_argument("-o", "--conta", dest="conta_id", type=int, \
        help="Ao iniciar abre a conta com o ID indicado, se ela existir.")

    args = parser.parse_args()

    app = MainApp(
        drop_tables=args.drop,
        populate_sample=args.sample,
        open_conta_id=args.conta_id
    )
    sys.exit(app.app.exec_())
