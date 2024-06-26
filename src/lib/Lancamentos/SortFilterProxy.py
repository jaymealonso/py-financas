import moment
from datetime import datetime
from PyQt5.QtCore import QModelIndex, QObject, QSortFilterProxyModel, QRegExp, Qt
import moment.utils


class FilterCategoria:
    def __init__(self, categoria: str) -> None:
        self.categoria = categoria
        self.filter_categoria = None

    def validate(self, categoria: str) -> bool:
        regex = QRegExp(self.categoria, Qt.CaseInsensitive, QRegExp.RegExp)
        return regex.indexIn(categoria) > -1


class FilterAnoMes:
    def __init__(self, ano_mes: str) -> None:
        self.filter_data_inicio = None
        self.filter_data_final = None
        self.calculate_start_end(ano_mes)

    def calculate_start_end(self, ano_mes: str):
        try:
            ano = int(ano_mes[0:4])
            mes = int(ano_mes[5:7])
        except Exception as e:
            return

        prox_ano = ano + 1 if mes == 12 else ano
        prox_mes = mes + 1 if mes < 12 else 1

        self.filter_data_inicio = moment.date(ano, mes, 1)
        self.filter_data_final = moment.date(prox_ano, prox_mes, 1).add(day=-1)

    def validate(self, date_moment: moment.Moment) -> bool:
        return (
            date_moment >= self.filter_data_inicio
            and date_moment <= self.filter_data_final
        )


class LancamentoSortFilterProxyModel(QSortFilterProxyModel):

    def __init__(self, parent: QObject | None = ...) -> None:
        super(LancamentoSortFilterProxyModel, self).__init__(parent)

        self.filters = []
        self.setSortRole(Qt.UserRole)

    def clear_filters(self):
        self.filters.clear()

    def add_filter(self, ano_mes: str, categoria: str):
        self.filters.append({0: FilterAnoMes(ano_mes), 1: FilterCategoria(categoria)})

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        if len(self.filters) == 0:
            return True

        categoria = self.sourceModel().index(source_row,  6, source_parent).data()

        date_date: datetime = (
            self.sourceModel().index(source_row, 5, source_parent).data(Qt.UserRole)
        )
        date_moment: moment.Moment = moment.date(date_date)

        for single_filter in [x for x in self.filters]:
            single_filter_aux = list(dict.values(single_filter))
            filter_ano_mes = single_filter_aux[0]
            filter_categoria = single_filter_aux[1]

            if not isinstance(filter_categoria, FilterCategoria) or not isinstance(
                filter_ano_mes, FilterAnoMes
            ):
                continue

            if filter_ano_mes.validate(date_moment) and filter_categoria.validate(
                categoria
            ):
                return True
        return False

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        # se existir texto acessivel (que ja foi tratado para ser usado como ordenacao)
        # usa ele para ordenação
        if left.data(Qt.AccessibleTextRole):
            return left.data(Qt.AccessibleTextRole) < right.data(Qt.AccessibleTextRole)

        return super().lessThan(left, right)

    

