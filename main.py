
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from PyQt5.QtWidgets import *  # QApplication, QLabel, QWidget, Q
from view.main_window import MainWindow


class MainApp:
    def __init__(self):
        self.app = QApplication([])
        self.app.setStyle('Fusion')
        self.app.setStyleSheet('QWidget {font-size: 24px}')

        self.window = MainWindow() # QMainWindow() #  QWidget()
        self.window.show()

app = MainApp()
app.app.exec_()
