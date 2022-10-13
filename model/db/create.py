import os
from sqlalchemy import create_engine
from db_orm import Base
import sys

path = os.path.dirname(os.path.abspath(__file__))
print(path)
engine = create_engine(f"sqlite://{path}/database.db", echo=True, future=True)
# engine = create_engine(
#     "sqlite:///home/jayme/Documentos/devs/py-financas/model/db/database.db",
#     echo=True,
#     future=True,
# )


def drop_all():
    print("=====================================")
    print("Eliminando todas as tabelas")
    print("=====================================")
    Base.metadata.drop_all(engine)


def create():
    print("=====================================")
    print("Criando banco de dados...(create_all)")
    print("=====================================")
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    if "--drop" in sys.argv:
        drop_all()
    create()
