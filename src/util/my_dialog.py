from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QDialog, QWidget


class MyDialog(QDialog):
    # sender: QDialog
    on_close_signal = pyqtSignal(QDialog)

    def __init__(self, parent: QWidget):
        super(MyDialog, self).__init__(parent)

        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

    def keyPressEvent(self, event):
        """Fecha a janela mas salva a geometria dela quando apertar o ESC"""
        if event.key() == Qt.Key_Escape:
            self.on_close_signal.emit(self)
        super(MyDialog, self).keyPressEvent(event)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.on_close_signal.emit(self)
