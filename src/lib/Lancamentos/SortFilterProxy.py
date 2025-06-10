import moment
import moment.utils

from lib import logging
from typing import List, cast
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QWidget
from datetime import datetime
from PyQt5.QtCore import QAbstractItemModel, QMimeData, QModelIndex, QObject, QRegExp, Qt, pyqtSignal
from PyQt5.QtWidgets import QAbstractItemView

from lib.Genericos.MySortFilterProxyModel import MySortFilterProxyModel


class FilterAllTable:
    def __init__(self, text: str) -> None:
        self.text = text

    def validate(self, text: str) -> bool:
        regex = QRegExp(self.text, Qt.CaseSensitivity.CaseInsensitive, QRegExp.FixedString)
        return regex.indexIn(text) > -1


class FilterCategoria:
    def __init__(self, categoria: str) -> None:
        self.filtered_categoria = categoria or "(vazio)"
        self.filter_categoria = None

    def validate(self, validating_categoria: str) -> bool:
        regex = QRegExp(self.filtered_categoria, Qt.CaseSensitivity.CaseInsensitive, QRegExp.FixedString)
        return regex.indexIn(validating_categoria) > -1


class FilterAnoMes:
    def __init__(self, ano_mes: str) -> None:
        self.filter_data_inicio = None
        self.filter_data_final = None
        self.calculate_start_end(ano_mes)

    def calculate_start_end(self, ano_mes: str):
        """Calculate start and end date for the filter"""
        try:
            ano = int(ano_mes[0:4])
            mes = int(ano_mes[5:7])
        except Exception as e:  # noqa: F841
            return

        prox_ano = ano + 1 if mes == 12 else ano
        prox_mes = mes + 1 if mes < 12 else 1

        self.filter_data_inicio = moment.date(ano, mes, 1)
        self.filter_data_final = moment.date(prox_ano, prox_mes, 1).add(day=-1)

    def validate(self, date_moment: moment.Moment) -> bool:
        return date_moment >= self.filter_data_inicio and date_moment <= self.filter_data_final


class LancamentoSortFilterProxyModel(MySortFilterProxyModel):
    """Proxy model for LancamentosView"""

    # prev_lancamento_id, next_lancamento_id
    dropped_lancamento = pyqtSignal(int, int)
    """Signal emitted when a lancamento is dropped here from drag and drop"""

    def __init__(self, parent: QObject | None = None) -> None:
        super(LancamentoSortFilterProxyModel, self).__init__(parent)

        self.filters: List[dict[int, FilterAnoMes | FilterCategoria]] = []
        self.text_filters: List[dict[int, FilterAllTable]] = []

    def clear_filters(self):
        self.filters.clear()
        self.text_filters.clear()

    def filter_text(self, text: str) -> None:
        self.text_filters.clear()
        self.text_filters.append({0: FilterAllTable(text)})

    def add_filter(self, ano_mes: str, categoria: str):
        self.filters.append({0: FilterAnoMes(ano_mes), 1: FilterCategoria(categoria)})

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        COLUNA_CATEGORIA_INDEX = 6
        COLUNA_DATA_INDEX = 5

        src_model: QStandardItemModel = cast(QStandardItemModel, self.sourceModel())

        if len(self.text_filters) == 0 and len(self.filters) == 0:
            return True

        if len(self.text_filters) > 0:
            # search in all columns
            for col_index in range(src_model.columnCount()):
                text = src_model.index(source_row, col_index, source_parent).data()
                single_filter = list(dict.values(self.text_filters[0]))[0]
                if single_filter.validate(text):
                    return True

        if len(self.filters) > 0:
            categoria = src_model.index(source_row, COLUNA_CATEGORIA_INDEX, source_parent).data()
            date_date: datetime = src_model.index(source_row, COLUNA_DATA_INDEX, source_parent).data(
                Qt.ItemDataRole.UserRole
            )
            if not date_date:
                return True
            date_moment: moment.Moment = moment.date(date_date)

            for single_filter in [x for x in self.filters]:
                single_filter_aux = list(single_filter.values())
                filter_ano_mes = single_filter_aux[0]
                filter_categoria = single_filter_aux[1]

                if not isinstance(filter_categoria, FilterCategoria) or not isinstance(filter_ano_mes, FilterAnoMes):
                    continue

                if filter_ano_mes.validate(date_moment) and filter_categoria.validate(categoria):
                    return True

        return False

    def dropMimeData(
        self, data: QMimeData | None, action: Qt.DropAction, row: int, column: int, parent: QModelIndex
    ) -> bool:
        logging.debug(f"""LancamentoSortFilterProxyModel->dropMimeData 
                          row: {row} column: {column}, action: {action}, modelindex: {parent.row()}/{parent.column()}""")

        # In between rows
        if parent.row() == -1 and parent.column() == -1 and action == Qt.DropAction.MoveAction:
            lanc_view = cast(QWidget, self.parent())
            model = cast(QAbstractItemModel, lanc_view.table.model())
            if row == 0:
                row = 1
            lancamento_id_index = model.index(row - 1, 0)
            lancamento_id = lancamento_id_index.data(Qt.ItemDataRole.UserRole)
            seq_linha = model.index(row, 1).data(Qt.ItemDataRole.UserRole)
            next_lancamento_id = lancamento_id_index.sibling(row, 0).data(Qt.ItemDataRole.UserRole)
            logging.debug(f"lancamento_id: {lancamento_id}, next:{next_lancamento_id}, seq: {seq_linha}")

            if lanc_view.table.dropIndicatorPosition() in [
                QAbstractItemView.DropIndicatorPosition.OnItem,
                QAbstractItemView.DropIndicatorPosition.OnViewport,
            ]:
                logging.debug(f"Item solto fora do alvo permitido. {lanc_view.table.dropIndicatorPosition()}")
                return True

            if lancamento_id:
                self.dropped_lancamento.emit(lancamento_id, next_lancamento_id)

        return True  # result

    def supportedDropActions(self) -> Qt.DropActions:
        # super().supportedDropActions()
        return Qt.DropActions(Qt.DropAction.MoveAction)

    def lessThan(self, left, right):
        return super().lessThan(left, right)
