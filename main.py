from PyQt5.QtWidgets import QApplication
from view.main_window import MainWindow


class MainApp:
    def __init__(self):
        self.app = QApplication([])
        self.app.setStyle('Fusion')
        self.app.setStyleSheet('QWidget {font-size: 24px}')

        self.window = MainWindow()
        self.window.show()


app = MainApp()
app.app.exec_()
