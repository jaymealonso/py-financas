import logging
from enum import StrEnum

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, \
    QPushButton, QComboBox, QLineEdit, QGridLayout, QMessageBox, QFileDialog
from PyQt5.QtCore import Qt

from util.my_dialog import MyDialog
from util.settings import Settings


class TEXTS(StrEnum):
    TITLE = "Configuração"
    THEME = "Tema"
    DB_LOCATION = "Diretório da base de dados"
    SEARCH_FILE = "Procurar..."
    CHANGE_WARNING = "Modificações só entrarão em efeito quando sair e entrar aplicativo novamente."
    SAVE = "Salvar"
    CLOSE = "Fechar"
    SAVE_SUCCESS_TITLE = "Sucesso"
    SAVE_SUCCESS = "Configuração salva com exito."
    THEME_SYSTEM_DEFAULT = "Padrão do sistema"
    THEME_DARK = "Escuro"
    THEME_LIGHT = "Claro"


class ConfiguracaoView(MyDialog):
    def __init__(self, parent: QWidget):
        super(ConfiguracaoView, self).__init__(parent)

        self.setWindowFlag(Qt.WindowMinimizeButtonHint, False)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)

        self.setWindowTitle(TEXTS.TITLE)
        self.setFixedWidth(900)
        # self.setFixedHeight(200)

        components = ConfiguracaocComponents(self)
        self.global_settings = Settings()
        self.combo_themes = components.new_theme_combo(self.global_settings.get_theme_ini_value())
        self.db_location_text = components.new_db_location_text(self.global_settings.db_location)
        self.db_location_button = components.new_db_location_search_button()
        widget_db_location = components.pack_in_hbox([self.db_location_text, self.db_location_button])

        self.layout = QGridLayout()
        components.add_field(TEXTS.THEME, self.combo_themes)
        components.add_field(TEXTS.DB_LOCATION, widget_db_location)
        components.add_message(f"⚠ {TEXTS.CHANGE_WARNING}")
        components.add_buttons()
        self.setLayout(self.layout)

    def on_select_db_file(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        (file_name, selectedFilter) = dialog.getOpenFileName()
        if file_name:
            self.db_location_text.setText(file_name)

    def on_save_pressed(self) -> None:
        index = self.combo_themes.currentIndex()
        theme = self.combo_themes.itemData(index)
        logging.info(f"Salvando tema: {theme}")
        self.global_settings.theme = theme

        db_location = self.db_location_text.text()
        logging.info(f"Salvando db_location: {db_location}")
        self.global_settings.db_location = db_location

        QMessageBox.information(self, TEXTS.SAVE_SUCCESS_TITLE, TEXTS.SAVE_SUCCESS)
        self.close()

    def on_close_pressed(self) -> None:
        self.close()


class ConfiguracaocComponents:
    def __init__(self, parent: ConfiguracaoView):
        self.parent = parent
        self.layout_row_index = -1

    def new_theme_combo(self, valor: str) -> QComboBox:
        combo = QComboBox()
        combo.addItem(TEXTS.THEME_SYSTEM_DEFAULT, "")
        combo.addItem(TEXTS.THEME_DARK, "dark")
        combo.addItem(TEXTS.THEME_LIGHT, "light")
        indexes = combo.model().match(combo.model().index(0, 0), Qt.UserRole, valor)
        if len(indexes) > 0:
            index = indexes[0]
            combo.setCurrentIndex(index.row())
        return combo

    def new_db_location_text(self, db_path: str) -> QLineEdit:
        edit = QLineEdit(db_path)
        edit.setReadOnly(True)
        return edit

    def new_db_location_search_button(self) -> QPushButton:
        button_procurar = QPushButton(TEXTS.SEARCH_FILE)
        button_procurar.pressed.connect(lambda: self.parent.on_select_db_file())
        button_procurar.setFixedWidth(150)
        return button_procurar

    def pack_in_hbox(self, widgets: list[QWidget]) -> QWidget:
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        for widget in widgets:
            layout.addWidget(widget)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def add_field(self, label: str, widget: QWidget) -> None:
        self.layout_row_index += 1
        self.parent.layout.addWidget(QLabel(label), self.layout_row_index, 0)
        self.parent.layout.addWidget(widget, self.layout_row_index, 1)

    def add_buttons(self) -> None:
        self.layout_row_index += 1
        widget = QWidget()
        layout = QHBoxLayout()

        layout.addStretch()

        button_save = QPushButton(TEXTS.SAVE)
        button_save.setFixedWidth(100)
        button_save.pressed.connect(lambda: self.parent.on_save_pressed())
        layout.addWidget(button_save)

        button_close = QPushButton(TEXTS.CLOSE)
        button_close.setFixedWidth(100)
        button_close.pressed.connect(lambda: self.parent.on_close_pressed())
        layout.addWidget(button_close)

        widget.setLayout(layout)
        self.parent.layout.addWidget(widget, self.layout_row_index, 0, 1, 2)

    def add_message(self, msg: str):
        self.layout_row_index += 1
        widget = QWidget()
        layout = QHBoxLayout()
        text = QLabel(msg)
        layout.addWidget(text)
        widget.setLayout(layout)
        self.parent.layout.addWidget(widget, self.layout_row_index, 0, 1, 2)