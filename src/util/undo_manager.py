
from lib.Genericos.log import logging

class class_undo_manager:
    def __init__(self):
        self._history = {
            "undo": [],
            "redo": []
        }

    def register(self, undo_command, *args, **kwargs): 
        """ Registra um comando que foi executado """
        self._history["undo"].append((undo_command, args, kwargs))

    def undo(self) -> bool:
        if len(self._history["undo"]) < 1:
            logging.error("Nada a desfazer. Pilha vazia.")
            return False

        command, args, kwargs = self._history["undo"][-1]
        if not command:
            logging.error("Nada a desfazer. Commando não encontrado.")
            return False
        else:
            try:
                command(*args, **kwargs)
                self._history["undo"].pop()
                logging.info("Desfeito com sucesso.")
                return True
            except Exception as e:
                logging.error(f"Erro: {e}")
                return False

# criar uma instancia que sera usada no programa todo
manager = class_undo_manager()
