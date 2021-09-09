# import Lancamento
import os
import pandas as pd

class TipoDeConta:
    def __init__(self):
        path = os.path.dirname(os.path.abspath(__file__))
        self.tipo_de_conta = pd.read_json(path + r".\initial_load\tipo_conta.json", orient="split")

    def get_descricao(self, tp_conta):
        return self.tipo_de_conta[""]


class Conta:
    def __init__(self, _id, descricao, tipo_de_conta, id_banco):
        self._id = _id
        self.descricao = descricao
        self.tipo_de_conta = tipo_de_conta
        self.id_banco = id_banco

    # def add_lancamento(self):
    #     self.lancamentos.append(Lancamento())
