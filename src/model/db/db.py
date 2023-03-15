from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from pathlib import Path
from model.db.db_orm import Base
from model.initial_load.initial_db_data import DataLoader

# DATABASE_FILE = Path.cwd() / "src" / "model" / "db" / "database.db"
DATABASE_FILE = Path.cwd() / "database.db"


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Database(metaclass=SingletonMeta):
    def __init__(self):
        print(f"Conectando a base de dados: {DATABASE_FILE}")
        self.engine:Engine = create_engine(f"sqlite:///{DATABASE_FILE}", echo=True)

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
        with self.engine.connect() as conn:                
            Base.metadata.drop_all(conn)

    def create_structure(self) -> None:
        print("=====================================")
        print("Criando banco de dados...(create_all)")
        print("=====================================")
        with self.engine.connect() as conn:        
            Base.metadata.create_all(conn)

    def is_initial_load(self) -> bool:
        """
        Verifica se a tabela "contas_tipo" já foi criada, se sim o banco já
        tem os metadados preenchidos
        """
        with self.engine.connect() as conn:
            return self.engine.dialect.has_table(conn, 'contas_tipo')

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
