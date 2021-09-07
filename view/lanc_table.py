from PyQt5.QtWidgets import QTableWidget


class LancamentosTable(QTableWidget):
    def __init__(self):
        super(LancamentosTable, self).__init__()
        self.setColumnCount(4)
        self.setRowCount(4)