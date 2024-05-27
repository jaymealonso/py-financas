from PyQt5.QtCore import QModelIndex, QObject, QSortFilterProxyModel, Qt


class MySortFilterProxyModel(QSortFilterProxyModel):

    def __init__(self, parent: QObject | None = ...) -> None:
        super(MySortFilterProxyModel, self).__init__(parent)

        self.setSortRole(Qt.UserRole)

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        # se existir texto acessivel (que ja foi tratado para ser usado como ordenacao)
        # usa ele para ordenação
        if left.data(Qt.AccessibleTextRole):
            return left.data(Qt.AccessibleTextRole) < right.data(Qt.AccessibleTextRole)

        return super().lessThan(left, right)
