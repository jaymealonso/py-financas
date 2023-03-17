import locale

locale.setlocale(locale.LC_ALL, "pt_BR.utf8")


def str_curr_to_locale(value_in: str | int) -> str:
    if isinstance(value_in, str):
        value_in = str_curr_to_int(value_in) 
    value:float = float(value_in/ 100)

    return locale.currency(val=value, symbol=False, grouping=True)


def str_curr_to_int(value: str) -> int:
    """
    Recebe valor numerico em texto e converte ele para inteiro com 2 decimais
    """
    # se for vazio ou somente um "-" retorna 0
    text:str = value
    if text.replace("-", "").strip() == "":
        return 0
    
    value_float:float = round(locale.atof(text),2)
    value_int:int = locale.atoi(str(int(value_float * 100)))
    return value_int


def int_to_locale(value_int: int) -> str:
    value_f: float = value_int / 100
    str_formatted = locale.currency(val=value_f, symbol=False, grouping=True)
    str_formatted = str_formatted.strip()
    return str_formatted
