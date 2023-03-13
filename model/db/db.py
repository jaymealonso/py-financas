from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from pathlib import Path
from model.db.db_orm import Base
from model.initial_load.initial_db_data import DataLoader

DATABASE_FILE = Path.cwd() / "model" / "db" / "database.db"


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Database(metaclass=SingletonMeta):
    def __init__(self):
        self.engine: Engine = self.connect()

    def connect(self) -> Engine:
        print(f"Conectando a base de dados: {DATABASE_FILE}")
        engine = create_engine(f"sqlite:///{DATABASE_FILE}", echo=True)
        return engine

    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """
        Turn Foreing keys ON for SQLite, executes always when a new connection
        is open.
        """
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    def drop_all(self) -> None:
        print("=====================================")
        print("Eliminando todas as tabelas")
        print("=====================================")
        Base.metadata.drop_all(self.engine)

    def create_structure(self) -> None:
        print("=====================================")
        print("Criando banco de dados...(create_all)")
        print("=====================================")
        Base.metadata.create_all(self.engine)

    def is_initial_load(self) -> bool:
        """
        Verifica se a tabela "contas_tipo" já foi criada, se sim o banco já
        tem os metadados preenchidos
        """
        return "contas_tipo" in self.engine.table_names()

    def run_initial_load(self, populate_sample: bool):
        startup = DataLoader(self.engine)
        if not self.is_initial_load():
            self.create_structure()
            startup.insert_all()
        else:
            print("Dados já carregados, pulando Initial load")
            print("------------------------")

        if populate_sample:
            print("Populando dados de exemplo")
            print("------------------------")
            startup.insert_sample_db()
