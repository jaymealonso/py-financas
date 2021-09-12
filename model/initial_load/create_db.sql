
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

-- DELETE TABELAS EXISTENTES
--------------------------------------------------------------------------------
DROP TABLE IF EXISTS contas_tipo;
DROP TABLE IF EXISTS contas;
DROP TABLE IF EXISTS lancamentos;

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
    valor TYPE NUMERIC NOT NULL
);

-- CREATE UNIQUE INDEX lancamentos_nr_referencia ON lancamentos(conta_id,nr_referencia);

-- DADOS MESTRE
--------------------------------------------------------------------------------
INSERT INTO contas_tipo VALUES (1, 'Conta Corrente');
INSERT INTO contas_tipo VALUES (2, 'Poupança');
INSERT INTO contas_tipo VALUES (3, 'Cartão crédito');

-- BANCO DE EXEMPLO
--------------------------------------------------------------------------------
INSERT INTO contas VALUES (null, 'Itaú-CC', '0516-145589', 'BRL', 1);
INSERT INTO contas VALUES (null, 'ActivoBank-CC', 'PT144684831', 'EUR', 1);
INSERT INTO contas VALUES (null, 'ActivoBank-CRD', 'PT144684831','EUR',  3);
INSERT INTO contas VALUES (null, 'BPI-CC', '4477889-888555', 'EUR', 1);

INSERT INTO lancamentos VALUES (null, 1, "334562", "Transf China", '2019-11-30', -2000.00);
INSERT INTO lancamentos VALUES (null, 1, "334563", "Transf Port.", '2019-11-30', -120.00);

INSERT INTO lancamentos VALUES (null, 2, "334562", "Salario", '2019-11-30', 5000.00);
INSERT INTO lancamentos VALUES (null, 2, "334563", "Compra bala", '2019-11-30', -100.00);
INSERT INTO lancamentos VALUES (null, 2, "334564", "Comprar chiclete", '2019-11-30', -120.00);
INSERT INTO lancamentos VALUES (null, 2, "334565", "Aluguel", '2019-12-01', -650.50);
INSERT INTO lancamentos VALUES (null, 2, "334566", "Carro", '2019-12-02', -360.50);

COMMIT;
