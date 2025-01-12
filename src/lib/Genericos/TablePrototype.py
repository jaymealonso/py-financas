from collections.abc import ItemsView
from abc import ABC


class ColumnNotFound(Exception):
    pass


class ColumnDefinition:
    def __init__(self, title: str = "", sql_colname: str = "", width: int = 100):
        self._title = title
        self._sql_colname = sql_colname
        self._width = width

    @property
    def title(self) -> str:
        return self._title

    @property
    def sql_colname(self) -> str:
        return self._sql_colname

    @property
    def width(self) -> int:
        return self._width


type_colindex = int
type_column = dict[type_colindex, ColumnDefinition]


class TableColumnsProvider(ABC):
    def __init__(self, columns: type_column) -> None:
        self._columns: dict[type_colindex, ColumnDefinition] = columns

    def count(self) -> int:
        return len(self._columns)

    def column(self, col_index: type_colindex) -> ColumnDefinition:
        column = self._columns.get(col_index)
        if not column:
            raise ColumnNotFound(f"Column with index {col_index} not found")
        return column

    def all(self) -> ItemsView[type_colindex, ColumnDefinition]:
        return self._columns.items()

    def titles(self) -> list[str]:
        """Return the titles of all columns"""
        return [col.title for col in self._columns.values()]
