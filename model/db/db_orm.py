from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import Table
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class ContasTipo(Base):
    __tablename__ = "contas_tipo"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    descricao = Column(String)


class Contas(Base):
    __tablename__ = "contas"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    descricao = Column(String)
    numero = Column(String)
    moeda = Column(String)

    tipo_id = Column(Integer, ForeignKey("contas_tipo.id"), nullable=False)
    Tipo = relationship("ContasTipo")


association_lanc_categ = Table(
    "lancamentos_categorias",
    Base.metadata,
    Column("lancamento_id", ForeignKey("lancamentos.id"), primary_key=True),
    Column("categoria_id", ForeignKey("categorias.id"), primary_key=True),
)


class Lancamentos(Base):
    __tablename__ = "lancamentos"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    nr_referencia = Column(String)
    descricao = Column(String)
    data = Column(DateTime)
    valor = Column(Integer)

    conta_id = Column(Integer, ForeignKey("contas_tipo.id"), nullable=False)
    Conta = relationship("Contas")
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    Categorias = relationship("Categorias", secondary=association_lanc_categ)


class Categorias(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    nm_categoria = Column(String)

    lancamento_id = Column(Integer)
    Lancamentos = relationship("Lancamentos", secondary=association_lanc_categ)


class Anexos(Base):
    __tablename__ = "anexos"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    descricao = Column(String)
    caminho = Column(String)

    lancamento_id = Column(Integer, ForeignKey("lancamentos.id"), nullable=False)
    Lancamento = relationship("Lancamentos")
