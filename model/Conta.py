import Lancamento

class TipoDeConta:
    CONTA_CORRENTE = "ccorr"
    CONTA_POUPANCA = "ccorr"
    CONTA_DEBITO = "cdebi"
    CONTA_CREDITO = "ccred"

    def __init__(self):
        self.tipo_de_conta = {
            self.CONTA_CORRENTE: "Conta Corrente",
            self.CONTA_POUPANCA: "Conta Poupança",
            self.CONTA_DEBITO: "Conta Débito",
            self.CONTA_CREDITO: "Conta Crédito"
        }

    def get_descricao(self, tp_conta):
        return self.tipo_de_conta[tp_conta]


class Conta:
    def __init__(self, id, descricao, tipo_de_conta, id_banco):
        self._id = id
        self.descricao = descricao
        self.tipo_de_conta = tipo_de_conta
        self.id_banco = id_banco

    def add_lancamento(self):
        self.lancamentos.append(Lancamento())
