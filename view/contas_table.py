from PyQt5.QtWidgets import QTableWidget


class ContasTable(QTableWidget):
    def __init__(self):
        super(ContasTable, self).__init__()
        self.setColumnCount(4)
        self.setRowCount(4)
