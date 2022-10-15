# from model.Conta import Conta, Contas
from model.Conta import Conta, Contas


def test_conta_select_data():
    contas = Contas()
    assert len(contas.items()) == 0

    contas.load()
    assert len(contas.items()) != 0
