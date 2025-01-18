from typing import cast
import view.icons.icons as icons
from PyQt5.QtWidgets import QLineEdit, QPushButton
from lib import TableLine
from util import ComboBoxDelegate, QCurrencyLineEdit
from model import Categorias


class LancamentoTableLine(TableLine):
    def __init__(self, parent):
        super(LancamentoTableLine, self).__init__()
        # self.parentOne: LancamentosView = parent

        self.table = parent.table
        self.model_categorias = cast(Categorias, parent.model_categorias)

    # def get_currency_value_delegate(self) -> CurrencyEditDelegate:
    #     return CurrencyEditDelegate(self.table)

    def get_categoria_dropdown_delegate(self) -> ComboBoxDelegate:
        categorias = {}
        for item in self.model_categorias.items:
            categorias[item.id] = item.nm_categoria

        cmb_delegate = ComboBoxDelegate(categorias, self.table)

        return cmb_delegate

    # def get_date_input(self):
    #     date = DateEditDelegate(self.table)
    #     return date

    def get_currency_input(self, valor: int, row: int, col: int) -> QCurrencyLineEdit:
        line_edit = QCurrencyLineEdit(self.table)
        line_edit.setTextInt(valor)
        return line_edit

    # def on_curr_input_text_changed(self, *args, **kwargs) -> None:
    #     self.sender().setTextFormat()

    def get_label_for_saldo(self, value: int) -> QLineEdit:
        label = super().get_label_for_currency(value)
        return label

    @staticmethod
    def get_del_button() -> QPushButton:
        del_pbutt = QPushButton()
        del_pbutt.setToolTip("Eliminar Lançamento")
        del_pbutt.setIcon(icons.delete())
        return del_pbutt

    @staticmethod
    def get_attach_button() -> QPushButton:
        del_pbutt = QPushButton()
        del_pbutt.setToolTip("Anexos")
        del_pbutt.setIcon(icons.attach())
        return del_pbutt
