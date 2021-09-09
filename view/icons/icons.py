import os
from PyQt5.QtGui import QIcon, QPixmap

path = os.path.dirname(os.path.abspath(__file__))


def save():
    return QIcon(QPixmap(path + r".\icons\save_as.png"))


def add():
    return QIcon(QPixmap(path + r".\add.png"))


def delete():
    return QIcon(QPixmap(path + r".\delete.png"))


def open_folder():
    return QIcon(QPixmap(path + r".\delete.png"))

