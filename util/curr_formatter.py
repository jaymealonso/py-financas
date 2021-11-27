import locale

locale.setlocale(locale.LC_ALL, "pt_br")


def str_curr_to_locale(value: str) -> str:
    return int_to_locale(str_curr_to_int(value))


# def str_curr_to_float(value: str) -> float:
#     if value == "":
#         value = "0"
#     value_float = locale.atof(value)
#     return value_float


def str_curr_to_int(value: str) -> int:
    if value == "":
        value = "0"
    value = value.replace(".", "").replace(",", ".")  # 1.234,56 >> 1234.56
    value_int = locale.atoi(value)
    return value_int


# def float_to_locale(value_float: float) -> str:
#     str_formatted = locale.currency(val=value_float, symbol=False, grouping=True)
#     str_formatted = str_formatted.strip()
#     return str_formatted


def int_to_locale(value_int: int) -> str:
    value_f: float = value_int / 100
    str_formatted = locale.currency(val=value_f, symbol=False, grouping=True)
    str_formatted = str_formatted.strip()
    return str_formatted
