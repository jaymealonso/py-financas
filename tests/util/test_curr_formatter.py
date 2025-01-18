#
#

from util import str_curr_to_locale, str_curr_to_int, int_to_locale


def test_currency_to_localized_zero():
    formatted_value = str_curr_to_locale("")
    assert formatted_value == "0,00"


def test_currency_to_localized():
    formatted_value = str_curr_to_locale("1.234,98")
    assert formatted_value == "1.234,98"


def test_convert_formatted_curr_to_int():
    int = str_curr_to_int("1.445,99")
    assert int == 144599

    int = str_curr_to_int("22,00")
    assert int == 2200


def test_int_to_localized_value():
    local_str = int_to_locale(1890)
    assert local_str == "18,90"

    local_str = int_to_locale(23940087)
    assert local_str == "239.400,87"

    local_str = int_to_locale(0)
    assert local_str == "0,00"
