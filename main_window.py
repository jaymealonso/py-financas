from PyQt5.QtWidgets import *  # QApplication, QLabel, QWidget, Q


class MainWindow:
    def get_content(self):
        layout = QVBoxLayout()

        layout.addWidget(self.__get_toolbar())

        tabbar = QTabWidget()
        tabbar.addTab(self.__get_table(), "Contas")
        layout.addWidget(tabbar)

        return layout

    def __get_toolbar(self):
        toolbar = QToolBar()
        toolbar.addWidget(QPushButton('Load'))
        toolbar.addWidget(QPushButton('Save'))
        toolbar.addWidget(QPushButton('Exit'))

        return toolbar

    def __get_table(self):
        table = QTableWidget(0, 4)
        table.insertRow(0)
        table.insertRow(0)
        table.insertRow(0)
        table.insertRow(0)
        return table
