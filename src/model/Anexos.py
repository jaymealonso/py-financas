from datetime import date
from pathlib import Path
import shutil
from typing import List
from model.db.db import Database
from model.db.db_orm import Anexos as ORMAnexos, Lancamentos as ORMLancamentos
from sqlalchemy import insert
from sqlalchemy.orm import Session
from util.settings import get_root_path

class Anexos:
    def __init__(self, lancamento_id):
        self.__items: List[ORMAnexos] = []
        self.__db = Database()
        self.lancamento_id: int = lancamento_id

    @property
    def items(self) -> List[ORMAnexos]:
        return self.__items
    
    def get_anexos_lancamento(self, lancamento_id: int) -> list[ORMAnexos]:
        items = [anexo for anexo in self.items if lancamento_id == lancamento_id]
        return items

    def load(self) -> None:
        self.__items.clear()
        with Session(self.__db.engine) as session:
            self.__items = (
                session.query(ORMAnexos)
                .filter(ORMAnexos.lancamento_id == self.lancamento_id)
                .all()
            )

        storage_dir = Path(get_root_path(paths=["storage"]))
        files = list(storage_dir.glob("*/*/*"))
        for anexo in self.__items:
            caminhos = [file for file in files if file.name.split("_")[0] == anexo.id]
            anexo.caminho = str(caminhos[0])

        print("camimnho")

    def add_new(self, id: str, descricao: str, nome_arquivo: str, 
            lancamento_id: int) -> ORMAnexos:
        """
        Adiciona novo anexo ao DB com os dados de entrada enviados
        e retorna o ID do novo anexo
        """
        with Session(self.__db.engine) as session:
            new_anexo = session.scalar(
                insert(ORMAnexos).returning(ORMAnexos),
                [
                    {
                        "id": id,
                        "descricao": descricao,
                        # "caminho": caminho,
                        "nome_arquivo": nome_arquivo,
                        "lancamento_id": lancamento_id,
                    }
                ],
            )
            session.commit()

            return new_anexo

    def move_anexos(self, lancamento: ORMLancamentos, new_data: date):
        """ Move arquivos anexos e atualiza a base de dados """
        anexos = self.get_anexos_lancamento(lancamento.id)
        ano_mes_old = f"{lancamento.data.year}{lancamento.data.month:0>2}"
        ano_mes_new = f"{new_data.year}{new_data.month:0>2}"

        if ano_mes_old != ano_mes_new:
            for anexo in anexos:
                self._move_arquivos_anexos(lancamento, anexo, new_data)

    def _move_arquivos_anexos(self, lancamento:ORMLancamentos ,anexo: ORMAnexos, new_data: date):
        """ Move arquivos anexos para novo diretorio se ano/mes for diferente """
        origin_file = Path(get_root_path(paths=[
                "storage",
                f"{lancamento.data.year}",
                f"{lancamento.data.year}.{lancamento.data.month:0>2}",
                f"{anexo.id}_{anexo.nome_arquivo}" 
            ])
        )
        dest_file = Path(get_root_path(paths=[
                "storage",
                f"{new_data.year}",
                f"{new_data.year}.{new_data.month:0>2}",
                f"{anexo.id}_{anexo.nome_arquivo}" 
            ])
        )
        dest_file.parent.absolute().mkdir(parents=True, exist_ok=True)
        shutil.move(origin_file, dest_file)
        
        
