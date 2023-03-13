from model.db.db import Database
from model.db.db_orm import Lancamentos
from sqlalchemy.orm import Session, aliased

def main():
    db = Database()
    # conn = db.connect()
    ealias = aliased(Lancamentos)
    session = Session(db.engine)


    result = session.query(Lancamentos) \
        .filter(ealias.id.between(Lancamentos.id, Lancamentos.seq_ordem_linha)) \
        .filter(Lancamentos.id == None) \
        .all()

    print("=======================================================")
    print(f" registros: {len(result)}")
    print("=======================================================")

    for i in result:
        print(i)


main()