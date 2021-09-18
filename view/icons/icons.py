import os
from PyQt5.QtGui import QIcon, QPixmap

path = os.path.dirname(os.path.abspath(__file__))


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

