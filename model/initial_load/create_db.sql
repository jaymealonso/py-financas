
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

-- DELETE TABELAS EXISTENTES
--------------------------------------------------------------------------------
DROP TABLE IF EXISTS lancamento_categoria;
DROP TABLE IF EXISTS categorias;
DROP TABLE IF EXISTS lancamentos;
DROP TABLE IF EXISTS contas;
DROP TABLE IF EXISTS contas_tipo;

-- CREATE TABLES + CONSTRAINSTS
--------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS contas_tipo (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TYPE TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS contas (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT NOT NULL,
    numero TEXT NOT NULL,
	moeda type TEXT NOT NULL,
    tipo TYPE INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS lancamentos (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    conta_id TYPE INTEGER NOT NULL,
    nr_referencia TYPE TEXT NOT NULL,
    descricao type TEXT NOT NULL,
    data TYPE TEXT NOT NULL,
    valor TYPE INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS categorias (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    nm_categoria TYPE TEXT NOT NULL,
    UNIQUE(nm_categoria)
);

CREATE TABLE IF NOT EXISTS lancamento_categoria (
    lancamento_id INTEGER,
    categoria_id INTEGER,
    PRIMARY KEY (lancamento_id, categoria_id)
    CONSTRAINT fk_lancamento_id
        FOREIGN KEY (lancamento_id)
        REFERENCES lancamentos (_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS lancamento_anexos (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    lancamento_id INTEGER,
    ano TEXT NOT NULL,
    mes TEXT NOT NULL,
    descricao TEXT NOT NULL,
    caminho TEXT NOT NULL
);

COMMIT;

BEGIN TRANSACTION;

-- DADOS MESTRE
--------------------------------------------------------------------------------

INSERT INTO "contas_tipo" ("_id","descricao") VALUES (null,'Conta Corrente');
INSERT INTO "contas_tipo" ("_id","descricao") VALUES (null,'Poupança');
INSERT INTO "contas_tipo" ("_id","descricao") VALUES (null,'Cartão Crédito');

INSERT INTO "categorias" ("_id","nm_categoria") VALUES (null,'Almoço');
INSERT INTO "categorias" ("_id","nm_categoria") VALUES (null,'Aluguel');
INSERT INTO "categorias" ("_id","nm_categoria") VALUES (null,'Água');
INSERT INTO "categorias" ("_id","nm_categoria") VALUES (null,'Banco');
INSERT INTO "categorias" ("_id","nm_categoria") VALUES (null,'Carro');
INSERT INTO "categorias" ("_id","nm_categoria") VALUES (null,'Cartão Crédito');
INSERT INTO "categorias" ("_id","nm_categoria") VALUES (null,'Combo TV+Internet');
INSERT INTO "categorias" ("_id","nm_categoria") VALUES (null,'Comida fora');
INSERT INTO "categorias" ("_id","nm_categoria") VALUES (null,'Compras');
INSERT INTO "categorias" ("_id","nm_categoria") VALUES (null,'Entretenimento');
INSERT INTO "categorias" ("_id","nm_categoria") VALUES (null,'Escola');
INSERT INTO "categorias" ("_id","nm_categoria") VALUES (null,'Imposto');
INSERT INTO "categorias" ("_id","nm_categoria") VALUES (null,'Luz');
INSERT INTO "categorias" ("_id","nm_categoria") VALUES (null,'Multa');
INSERT INTO "categorias" ("_id","nm_categoria") VALUES (null,'Poupança');
INSERT INTO "categorias" ("_id","nm_categoria") VALUES (null,'Salário');
INSERT INTO "categorias" ("_id","nm_categoria") VALUES (null,'Saque');
INSERT INTO "categorias" ("_id","nm_categoria") VALUES (null,'Segurança Social');
INSERT INTO "categorias" ("_id","nm_categoria") VALUES (null,'Seguro');
INSERT INTO "categorias" ("_id","nm_categoria") VALUES (null,'Supermercado');
INSERT INTO "categorias" ("_id","nm_categoria") VALUES (null,'Transferência');
INSERT INTO "categorias" ("_id","nm_categoria") VALUES (null,'Transporte');
COMMIT;

BEGIN TRANSACTION;
-- BANCO DE EXEMPLO
--------------------------------------------------------------------------------
INSERT INTO contas VALUES (null, 'Itaú-CC', '0516-145589', 'BRL', 1);
INSERT INTO contas VALUES (null, 'ActivoBank-CC', 'PT144684831', 'EUR', 1);
INSERT INTO contas VALUES (null, 'ActivoBank-CRD', 'PT144684831','EUR',  3);
INSERT INTO contas VALUES (null, 'BPI-CC', '4477889-888555', 'EUR', 1);

INSERT INTO "lancamentos" ("_id","conta_id","nr_referencia","descricao","data","valor") VALUES (null,1,'334562','Transf China','2019-11-30',-2200);
INSERT INTO "lancamentos" ("_id","conta_id","nr_referencia","descricao","data","valor") VALUES (null,1,'334563','Transf Port.','2019-11-30',-120);

INSERT INTO "lancamentos" ("_id","conta_id","nr_referencia","descricao","data","valor") VALUES (null,2, '334562', 'Salário', '2019-11-30', 500000);
INSERT INTO "lancamentos" ("_id","conta_id","nr_referencia","descricao","data","valor") VALUES (null,2, '334563', 'Compra bala', '2019-11-30', -10000);
INSERT INTO "lancamentos" ("_id","conta_id","nr_referencia","descricao","data","valor") VALUES (null,2, '334564', 'Comprar chiclete', '2019-11-30', -12000);
INSERT INTO "lancamentos" ("_id","conta_id","nr_referencia","descricao","data","valor") VALUES (null,2, '334565', 'Aluguel', '2019-12-01', -65050);
INSERT INTO "lancamentos" ("_id","conta_id","nr_referencia","descricao","data","valor") VALUES (null,2, '334566', 'Carro', '2019-12-02', -36050);

INSERT INTO lancamento_categoria values (1, 1);
INSERT INTO lancamento_categoria values (2, 1);

COMMIT;
