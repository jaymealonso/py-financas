#Financas Pessoais em Python com Qt

Projeto de finanças pessoais em Python com PyQt5.
Este projeto se propõe a criar um **aplicativo de desktop** que faça o controle das financas pessoais com importação de extratos bancários e categorização de receitas e despesas.

Este projeto tem como inspiração o Microsoft Money mas com a adição de outras funcionalidades.

Outras funcionalidades (planejadas):

- [x] Visão Mensal: Exibição de tabela/planilha receitas e despesas no movimento bancário(extrato) agrupadas por categorias
- [x] Importar Lançamentos: Importação de XLS/XLSX com movimento bancário
- [ ] Exportar para Excel
- [ ] Agendamento de despesas recorrentes para controle do que foi pago
- [ ] Organização de uma estrututa de arquivos(PDF/IMG/Outros) em diretórios com fatura, comprovantes de pagamento e outros.
- [ ] Associação das despesas agendadas com os arquivos relacionados de fatura, comprovantes de pagamento e outros.

---

## Sumário

- [Icones em](#icones-em)
- [Setup](#setup)
  - [Instalar o Python](#instalar-o-python)
  - [Instalar o PyQt5](#instalar-o-pyqt5)
  - [Instalar o sqlite3](#instalar-o-sqlite3)
  - [Instalar o pyinstaller](#instalar-o-pyinstaller)
  - [Instalar o openpyxl](#instalar-o-openpyxl)
- [Para executar](#para-executar)

---

## Icones em

Os icones foram pegos desta coleção, provavelmente irão mudar no futuro.

> https://iconarchive.com/show/farm-fresh-icons-by-fatcow.html

## Setup

Para configurar o ambiente e executar o projeto deve-se instalar as bibliotecas abaixo:

### Instalar o Python

Baixar o python no link

> `https://www.python.org/downloads/`
>
> Obs:. Eu estou utilizando a versão 3.9.7

### Instalar o PyQt5

PyQt5 é uma biblioteca port do C++ para criação de interfaces visuais com janelas, botões, etc.
[mais sobre PyQt aqui](https://realpython.com/python-pyqt-gui-calculator/#understanding-pyqt)

> `pip install PyQt5`

### Instalar o SQLAlchemy

SQLAlchemy é a blblioteca de ORM(object relational mapping) que administra o acesso ao banco de dados sem precisar escrever os selects explicitamente.
[mais sobre SQLAlchemy aqui](https://www.sqlalchemy.org/) versão: 1.4.40

> pip install sqlalchemy

### Instalar moment

Moment é uma lib para tratar data e hora.

> pip install moment

### Instalar o pyinstaller

A Lib `pyinstaller` possibilita o empacotamento do script em um arquivo `.exe` e também pode gerar um arquivo de instalação.

> `pip install pyinstaller`

### Instalar o openpyxl

A biblioteca `openpyxl` é usado para importar e interpretar dados em arquivo excel (geralmente exportado pelo banco)

> `pip install openpyxl`

## Para executar

Para executar via console use o comando abaixo:

> `python main.py`

## Criar executavel

Para gerar um arquivo executável(`.exe`) no diretório `/dist`:

> `pyinstaller main.spec`
