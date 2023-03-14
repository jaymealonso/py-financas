from model.db.db import Database
from model.db.db_orm import Lancamentos, Anexos
from sqlalchemy import select
from sqlalchemy.sql import func
from sqlalchemy.orm import Session

def main():
    db = Database()
    # conn = db.connect()
    session = Session(db.engine)

    # result = session.query(Lancamentos) \
    #     .filter(ealias.id.between(Lancamentos.id, Lancamentos.seq_ordem_linha)) \
    #     .filter(Lancamentos.id == None) \
    #     .all()

    result = session.execute(
        select(Lancamentos, func.count(Anexos.id).label("count")) \
        .join(Lancamentos.Anexos, isouter=True) \
        .group_by(Lancamentos)
        # .filter(ealias.id.between(Lancamentos.id, Lancamentos.seq_ordem_linha)) \
        # .filter(Lancamentos.id == None) \
        # .all()
    ).all()

    print()
    print("=======================================================")
    print(f" registros: {len(result)}")
    print("=======================================================")
    print()

    new_result = []
    for r in result:
        lancamento, count = r
        lancamento.count = count
        new_result.append(lancamento)

    fields = ['conta_id', 'data', 'descricao', 'id', 'nr_referencia', 'seq_ordem_linha', 'valor', 'count']

    for t in fields:
        print("{:<20}".format(t), end="")
        print(" | ", end="")        
    print("", end="\n")        

    for r in new_result:
        for t in fields:
            value =  r.__getattribute__(t) or ""
            print("{:>20}".format(str(value)), end="")
            print(" | ", end="")
        # print("{:>20}".format(len(r.Anexos)), end="")
        print('', end="\n")        


main()