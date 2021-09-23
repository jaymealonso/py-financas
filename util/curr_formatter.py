import locale


def str_curr_to_locale(value: str) -> str:
    return float_to_locale(str_curr_to_float(value))


def str_curr_to_float(str: str) -> float:
    is_negative = "-" in str
    value = str.replace(".", "").replace(",", ".").replace("-", "").strip()
    value_float = float(value)
    if is_negative:
        value_float = value_float * -1
    return value_float


def float_to_locale(value_float: float) -> str:
    locale.setlocale(locale.LC_ALL, "pt-br")
    str_formatted = locale.currency(val=value_float, symbol=False, grouping=True)
    str_formatted = str_formatted.strip()
    return str_formatted
