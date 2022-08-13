import sqlite3
import os
import sys

path = os.path.dirname(os.path.abspath(__file__))
# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

DATABASE_FILENAME = os.path.join(application_path, 'database.db')
INITIAL_LOAD_FILENAME = os.path.join(path, "initial_load", "create_db.sql")

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = \
                super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Database(metaclass=SingletonMeta):
    def __init__(self):
        print(f"Connecting to {DATABASE_FILENAME}")
        self.db = sqlite3.connect(DATABASE_FILENAME)
        print(f"Connected!")

    def is_initial_load(self):
        try:
            tuple_result = self.db.execute("select count(*) from contas_tipo").fetchone()
            contas_lines = int(tuple_result[0])
        except:
            return False
        return contas_lines > 0

    def run_initial_load(self):
        if not self.is_initial_load():
            sql_command = ""
            sql_command = sql_command.join(line for line in open(INITIAL_LOAD_FILENAME, encoding="ISO-8859-1").readlines())
            print("Executando initial load!")
            print("------------------------")
            print(sql_command)
            self.db.executescript(sql_command)
            print("------------------------")
            print("Initial load finalizado")
        else:
            print("Dados já carregados pulando Initial load")
            print("------------------------")
