#Financas Pessoais em Python com Qt

Projeto de finanças pessoais em Python com PyQt5.
Este projeto se propõe a criar um **aplicativo de desktop** que faça o controle das financas pessoais com importação de extratos bancários e categorização de receitas e despesas. 

Este projeto tem como inspiração o Microsoft Money mas com a adição de outras funcionalidades.

Outras funcionalidades (planejadas):

- Exibição de tabela/planilha receitas e despesas no movimento bancário(extrato) agrupadas por categorias 
- Importação de XLS/XLSX com movimento bancário
- Exportação para Excel
- Agendamento de despesas recorrentes para controle do que foi pago
- Organização de uma estrututa de arquivos(PDF/IMG/Outros) em diretórios com fatura, comprovantes de pagamento e outros.
- Associação das despesas agendadas com os arquivos relacionados de fatura, comprovantes de pagamento e outros.

---

__TOC__

## Sumário
- [Icones em](##Icones em)
- [Setup](#setup)
  - [Instalar o Python](###Instalar o Python)
  - [Instalar o PyQt5](###Instalar o PyQt5) 
  - [Instalar o sqlite3](###Instalar o sqlite3)
  - [Instalar o pyinstaller](###Instalar o pyinstaller)
  - [instalar o pandas]
  - [instalar o openpyxl]
- [Para executar](##Para executar)

---

## Icones em
Os icones foram pegos desta coleção, provavelmente irão mudar no futuro.
> https://iconarchive.com/show/farm-fresh-icons-by-fatcow.html

## Setup
Para configurar o ambiente e executar o projeto deve-se instalar as bibliotecas abaixo:

### Instalar o Python
> Baixar o python no link
> `https://www.python.org/downloads/`
> 
> Obs:. Eu estou utilizando a versão 3.9.7 

### Instalar o PyQt5
> PyQt5 é uma biblioteca port do C++ para criação de interfaces visuais com janelas, botões, etc.
> 
> `pip install PyQt5`

### Instalar o SqLite3
> SqLite é um banco de dados simples que é utilizado para facilitar a persistência dos dados dentro do aplicativo
> 
> `pip install sqlite3`

### Instalar o pyinstaller
> A Lib `pyinstaller` possibilita o empacotamento do script em um arquivo `.exe`
> 
> `pip install pyinstaller`
 
## Para executar
Para executar via console use o comando abaixo:
> `python main.py`
 
## Criar executavel
Para gerar um arquivo executável(`.exe`) no diretório `/dist`:
>`pyinstaller main.spec`
