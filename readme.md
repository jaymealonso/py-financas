# Financas Pessoais em Python com Qt

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

<<<<<<< HEAD
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

=======
## <a name='Sumrio'></a>Sumário
<!-- vscode-markdown-toc -->
* [Sumário](#Sumrio)
* [Icones em](#Iconesem)
* [Setup](#Setup)
	* [Instalar o Python](#InstalaroPython)
	* [Instalar o PyQt5](#InstalaroPyQt5)
	* [Instalar o SqLite3](#InstalaroSqLite3)
	* [Instalar o pyinstaller](#Instalaropyinstaller)
	* [Instalar o openpyxl](#Instalaroopenpyxl)
* [Para executar](#Paraexecutar)
* [Criar executavel](#Criarexecutavel)
* [Instalar libs](#Instalarlibs)
* [Instalar locale do Portugues Brasil](#InstalarlocaledoPortuguesBrasil)
* [Para Build](#ParaBuild)
* [Executar](#Executar)
* [Instalar libs](#Instalarlibs-1)

<!-- vscode-markdown-toc-config
	numbering=false
	autoSave=true
	/vscode-markdown-toc-config -->
<!-- /vscode-markdown-toc -->

---

## <a name='Iconesem'></a>Icones em
>>>>>>> 70c2b1dc33bf535d4a9fc0799c4f8c07f95a3fab
Os icones foram pegos desta coleção, provavelmente irão mudar no futuro.

> https://iconarchive.com/show/farm-fresh-icons-by-fatcow.html

<<<<<<< HEAD
## Setup

Para configurar o ambiente e executar o projeto deve-se instalar as bibliotecas abaixo:

### Instalar o Python

=======
## <a name='Setup'></a>Setup
Para configurar o ambiente e executar o projeto deve-se instalar as bibliotecas abaixo:

### <a name='InstalaroPython'></a>Instalar o Python
>>>>>>> 70c2b1dc33bf535d4a9fc0799c4f8c07f95a3fab
Baixar o python no link

> `https://www.python.org/downloads/`
>
> Obs:. Eu estou utilizando a versão 3.9.7

<<<<<<< HEAD
### Instalar o PyQt5

=======
### <a name='InstalaroPyQt5'></a>Instalar o PyQt5
>>>>>>> 70c2b1dc33bf535d4a9fc0799c4f8c07f95a3fab
PyQt5 é uma biblioteca port do C++ para criação de interfaces visuais com janelas, botões, etc.
[mais sobre PyQt aqui](https://realpython.com/python-pyqt-gui-calculator/#understanding-pyqt)

> `pip install PyQt5`

<<<<<<< HEAD
### Instalar o SQLAlchemy

SQLAlchemy é a blblioteca de ORM(object relational mapping) que administra o acesso ao banco de dados sem precisar escrever os selects explicitamente.
[mais sobre SQLAlchemy aqui](https://www.sqlalchemy.org/) versão: 1.4.40

> pip install sqlalchemy

### Instalar moment

Moment é uma lib para tratar data e hora.

> pip install moment

### Instalar pytest/pytest-coverage

Para os testes usarei a biblioteca do pytest

> `pip intall pytest`

> `pip intall pytest-coverage`

### Instalar o pyinstaller

=======
### <a name='InstalaroSqLite3'></a>Instalar o SqLite3
SqLite é um banco de dados simples que é utilizado para facilitar a persistência dos dados dentro do aplicativo
> 
> `pip install sqlite3`

### <a name='Instalaropyinstaller'></a>Instalar o pyinstaller
>>>>>>> 70c2b1dc33bf535d4a9fc0799c4f8c07f95a3fab
A Lib `pyinstaller` possibilita o empacotamento do script em um arquivo `.exe` e também pode gerar um arquivo de instalação.

> `pip install pyinstaller`
<<<<<<< HEAD

### Instalar o openpyxl

=======
 
### <a name='Instalaroopenpyxl'></a>Instalar o openpyxl
>>>>>>> 70c2b1dc33bf535d4a9fc0799c4f8c07f95a3fab
A biblioteca `openpyxl` é usado para importar e interpretar dados em arquivo excel (geralmente exportado pelo banco)

> `pip install openpyxl`

<<<<<<< HEAD
## Para executar

Para executar via console use o comando abaixo:

> `python main.py`

## Criar executavel

Para gerar um arquivo executável(`.exe`) no diretório `/dist`:

> `pyinstaller main.spec`
=======
## <a name='Paraexecutar'></a>Para executar
Para executar via console use o comando abaixo:

> `python main.py`
 
## <a name='Criarexecutavel'></a>Criar executavel
Para gerar um arquivo executável(`.exe`) no diretório `/dist`:
>`pyinstaller main.spec`

# Para fazer build/executar

## <a name='Instalarlibs'></a>Instalar libs
```
pip install PyQt5
pip install openpyxl
```
## <a name='InstalarlocaledoPortuguesBrasil'></a>Instalar locale do Portugues Brasil

Verificar se existe ```pt_BR``` na lista de locales:
```
locale -a
```
Se não houver instalar com:
```
sudo apt-get install language-pack-gnome-pt language-pack-pt-base
```
Depois executar:
```
sudo dpkg-reconfigure locales
```
## <a name='ParaBuild'></a>Para Build
todo

## <a name='Executar'></a>Executar
```
python main.py
```

# Criar instalador
## <a name='Instalarlibs-1'></a>Instalar libs
```
pip install pyinstaller
```
>>>>>>> 70c2b1dc33bf535d4a9fc0799c4f8c07f95a3fab
