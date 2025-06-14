import os
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize

path = os.path.dirname(os.path.abspath(__file__))


def app_icon() -> QIcon:
    _app_icon = QIcon()
    _app_icon.addFile(f"{path}/app-icon-16.png", QSize(8, 8))
    _app_icon.addFile(f"{path}/app-icon-32.png", QSize(16, 16))
    return _app_icon


def save() -> QIcon:
    return QIcon(QPixmap(path + r"/save_as.png"))


def add() -> QIcon:
    pixmap_path = path + r"/add.png"
    return QIcon(QPixmap(pixmap_path))


def delete() -> QIcon:
    return QIcon(QPixmap(path + r"/delete.png"))


def load() -> QIcon:
    return QIcon(QPixmap(path + r"/open_folder.png"))


def import_file() -> QIcon:
    return QIcon(QPixmap(path + r"/book_go.png"))


def open_lancamentos() -> QIcon:
    return QIcon(QPixmap(path + r"/table.png"))


def configurar() -> QIcon:
    return QIcon(QPixmap(path + r"/cog.png"))


def atualizar() -> QIcon:
    return QIcon(QPixmap(path + r"/update.png"))


def visao_mensal() -> QIcon:
    return QIcon(QPixmap(path + r"/visao_mensal.png"))


def undo() -> QIcon:
    return QIcon(QPixmap(path + r"/arrow_undo.png"))


def redo() -> QIcon:
    return QIcon(QPixmap(path + r"/arrow_redo.png"))


def attach() -> QIcon:
    return QIcon(QPixmap(path + r"/attach.png"))


def abrir_anexo_arquivo() -> QIcon:
    return QIcon(QPixmap(path + r"/open_attachment.png"))


def abrir_anexo_diretorio() -> QIcon:
    return QIcon(QPixmap(path + r"/open_attach_dir.png"))


def exportar_planilha() -> QIcon:
    return QIcon(QPixmap(path + r"/export_excel.png"))


def cancel() -> QIcon:
    return QIcon(QPixmap(path + r"/cancel.png"))


def tab_search() -> QIcon:
    return QIcon(QPixmap(path + r"/table_tab_search.png"))


def results_next() -> QIcon:
    return QIcon(QPixmap(path + r"/resultset_next.png"))


def results_prev() -> QIcon:
    return QIcon(QPixmap(path + r"/resultset_previous.png"))


def filter_clear() -> QIcon:
    return QIcon(QPixmap(path + r"/filter_clear.png"))


def excel_imports() -> QIcon:
    return QIcon(QPixmap(path + r"/excel_imports.png"))


def select_all() -> QIcon:
    return QIcon(QPixmap(path + r"/to_do_list_checked_all.png"))


def deselect_all() -> QIcon:
    return QIcon(QPixmap(path + r"/to_do_list.png"))


def find_file_dialog() -> QIcon:
    return QIcon(QPixmap(path + r"/open_folder.png"))


def status_info() -> QIcon:
    return QIcon(QPixmap(path + r"/information.png"))


def status_warning() -> QIcon:
    return QIcon(QPixmap(path + r"/warning.png"))


def status_error() -> QIcon:
    return QIcon(QPixmap(path + r"/error.png"))


def status_ok() -> QIcon:
    return QIcon(QPixmap(path + r"/ok.png"))


def status_not_exec() -> QIcon:
    return QIcon(QPixmap(path + r"/ok_gray.png"))


def arrow_left() -> QIcon:
    return QIcon(QPixmap(path + r"/arrow_left.png"))
