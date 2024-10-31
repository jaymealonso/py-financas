from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QWidget, QToolBar

class CustomToolbar(QToolBar):
    def __init__(self):
        super(CustomToolbar, self).__init__()
        self.setIconSize(QSize(24, 24))
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
