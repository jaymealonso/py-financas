
from collections.abc import Callable


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
            print("nada a desfazer")
            return False

        command, args, kwargs = self._history["undo"][-1]
        if not command:
            print("nada a desfazer")
            return False
        else:
            try:
                command(*args, **kwargs)
                self._history["undo"].pop()
                return True
            except Exception as e:
                print(f"Error {e}")
                return False

# criar uma instancia que sera usada no programa todo
manager = class_undo_manager()