from PyQt5.QtWidgets import QApplication
from view.main_window import MainWindow
from model.db import Database


class MainApp:
    def __init__(self):
        self.app = QApplication([])
        self.app.setStyle('Fusion')
        self.app.setStyleSheet('QWidget {font-size: 24px}')

        self.db = Database()
        self.db.run_initial_load()
        self.window = MainWindow()
        self.window.show()


if __name__ == "__main__":
    app = MainApp()
    app.app.exec_()
