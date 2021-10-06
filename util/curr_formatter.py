import locale

locale.setlocale(locale.LC_ALL, "pt_br")


def str_curr_to_locale(value: str) -> str:
    return float_to_locale(str_curr_to_float(value))


def str_curr_to_float(value: str) -> float:
    if value == "":
        value = "0"
    value_float = locale.atof(value)
    return value_float


def float_to_locale(value_float: float) -> str:
    str_formatted = locale.currency(val=value_float, symbol=False, grouping=True)
    str_formatted = str_formatted.strip()
    return str_formatted
