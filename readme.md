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
Os icones foram pegos desta coleção, provavelmente irão mudar no futuro.

> https://iconarchive.com/show/farm-fresh-icons-by-fatcow.html

## <a name='Setup'></a>Setup
Para configurar o ambiente e executar o projeto deve-se instalar as bibliotecas abaixo:

### <a name='InstalaroPython'></a>Instalar o Python
Baixar o python no link

> `https://www.python.org/downloads/`
>
> Obs:. Eu estou utilizando a versão 3.9.7

### <a name='InstalaroPyQt5'></a>Instalar o PyQt5
PyQt5 é uma biblioteca port do C++ para criação de interfaces visuais com janelas, botões, etc.
[mais sobre PyQt aqui](https://realpython.com/python-pyqt-gui-calculator/#understanding-pyqt)

> `pip install PyQt5`

### <a name='InstalaroSqLite3'></a>Instalar o SqLite3
SqLite é um banco de dados simples que é utilizado para facilitar a persistência dos dados dentro do aplicativo
> 
> `pip install sqlite3`

### <a name='Instalaropyinstaller'></a>Instalar o pyinstaller
A Lib `pyinstaller` possibilita o empacotamento do script em um arquivo `.exe` e também pode gerar um arquivo de instalação.

> `pip install pyinstaller`
 
### <a name='Instalaroopenpyxl'></a>Instalar o openpyxl
A biblioteca `openpyxl` é usado para importar e interpretar dados em arquivo excel (geralmente exportado pelo banco)

> `pip install openpyxl`

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
