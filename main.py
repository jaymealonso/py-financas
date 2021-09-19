import sys
import view.icons.icons as icons
from PyQt5.QtWidgets import QApplication
from view.main_window import MainWindow
from model.db import Database


class MainApp:
    def __init__(self):
        self.app = QApplication([])
        self.app.setStyle('Fusion')
        self.app.setStyleSheet('QWidget {font-size: 24px}')

        self.app.setWindowIcon(icons.app_icon())

        self.db = Database()
        self.db.run_initial_load()
        self.window = MainWindow(self.app)
        self.window.show()


if __name__ == "__main__":
    app = MainApp()
    sys.exit(app.app.exec_())
