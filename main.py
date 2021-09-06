from PyQt5.QtWidgets import *  # QApplication, QLabel, QWidget, Q
from main_window import MainWindow

class MainApp:
    def __init__(self):
        self.app = QApplication([])
        self.app.setStyle('Fusion')

        self.window = QWidget()
        self.window.setMinimumSize(800, 600)

        self.window.setLayout(MainWindow().get_content())
        self.window.show()

app = MainApp()
app.app.exec_()

