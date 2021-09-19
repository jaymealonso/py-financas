import os
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize

path = os.path.dirname(os.path.abspath(__file__))


def app_icon():
    _app_icon = QIcon()
    _app_icon.addFile('view/icons/app-icon-16.png', QSize(16, 16))
    _app_icon.addFile('view/icons/app-icon-32.png', QSize(32, 32))
    return _app_icon


def save():
    return QIcon(QPixmap(path + r".\save_as.png"))


def add():
    return QIcon(QPixmap(path + r".\add.png"))


def delete():
    return QIcon(QPixmap(path + r".\delete.png"))


def load():
    return QIcon(QPixmap(path + r".\open_folder.png"))


def import_file():
    return QIcon(QPixmap(path + r".\book_go.png"))


def open_lancamentos():
    return QIcon(QPixmap(path + r".\table.png"))


def configurar():
    return QIcon(QPixmap(path + r".\cog.png"))


def atualizar():
    return QIcon(QPixmap(path + r".\update.png"))

