from lib import logging
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from model import DataLoader
from util import Settings, SingletonMeta

from .db_orm import Base


class Database(metaclass=SingletonMeta):
    def __init__(self):
        self.settings = Settings()

        database_path = self.settings.db_location
        logging.debug(f"Conectando a base de dados: {database_path}")
        self.engine = create_engine(f"sqlite:///{database_path}", echo=False)

    def exists(self) -> bool:
        try:
            self.engine.connect()
            with self.engine.connect() as conn:
                conn.execute(text("SELECT * FROM sqlite_master"))
            logging.info("Database check exists SUCCESS!")
            return True
        except Exception as _:
            logging.error("Database check exists FAILED!")
            return False

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
        logging.debug("=====================================")
        logging.debug("Eliminando todas as tabelas")
        logging.debug("=====================================")
        with self.engine.connect() as conn:
            Base.metadata.drop_all(conn)

    def create_structure(self) -> None:
        logging.debug("=====================================")
        logging.debug("Criando banco de dados...(create_all)")
        logging.debug("=====================================")
        with self.engine.connect() as conn:
            Base.metadata.create_all(conn)
        conn.commit()

    def is_initial_load(self) -> bool:
        """
        Verifica se a tabela "contas_tipo" já foi criada, se sim o banco já
        tem os metadados preenchidos
        """
        with self.engine.connect() as conn:
            return self.engine.dialect.has_table(conn, "contas_tipo")

    def run_initial_load(self, populate_sample: bool):
        startup = DataLoader(self.engine)
        if not self.is_initial_load():
            self.create_structure()
            startup.insert_all()
        else:
            logging.debug(" Dados já carregados, pulando Initial load")
            logging.debug("-------------------------------------------")

        if populate_sample:
            logging.debug("Populando dados de exemplo")
            logging.debug("--------------------------")
            startup.insert_sample_db()
