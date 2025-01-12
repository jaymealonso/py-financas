from PyQt5.QtWidgets import QMessageBox, QWidget


class MyMessagePopup(QMessageBox):
    def __init__(self, parent=None):
        super(MyMessagePopup, self).__init__(parent)
        if isinstance(parent, QWidget):
            self.title = parent.windowTitle()

    def error(self, text: str, title: str = "Erro") -> None:
        self.setIcon(QMessageBox.Critical)

        if not title:
            if self.title:
                title = self.title

        self.setWindowTitle(title)
        self.setText(text)
        self.exec_()

    def success(self, text: str):
        self.setIcon(QMessageBox.Information)
        if not self.title:
            self.title = "Sucesso"
        self.setWindowTitle(self.title)
        self.setText(text)
        self.exec_()

    def warn(self, text: str):
        self.setIcon(QMessageBox.Warning)
        if not self.title:
            self.title = "Atenção"
        self.setWindowTitle(self.title)
        self.setText(text)
        self.exec_()

    def info(self, text: str):
        self.setIcon(QMessageBox.Information)
        if not self.title:
            self.title = "Informação"
        self.setWindowTitle(self.title)
        self.setText(text)
        self.exec_()
