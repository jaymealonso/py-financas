import sys
import view.icons.icons as icons
from PyQt5.QtWidgets import QApplication
from view.main_window import MainWindow
from model.db.db import Database


class MainApp:
    def __init__(self, drop_tables: bool, populate_sample: bool):
        self.app = QApplication([])
        self.app.setStyle("Fusion")
        # self.app.setStyleSheet('QWidget {font-size: 24px}')

        self.app.setWindowIcon(icons.app_icon())

        self.db = Database()
        if drop_tables:
            self.db.drop_all()
        self.db.run_initial_load(populate_sample)
        self.window = MainWindow(self.app)
        self.window.show()


if __name__ == "__main__":
    app = MainApp(
        drop_tables="--drop" in sys.argv, populate_sample="--sample" in sys.argv
    )
    sys.exit(app.app.exec_())
