
# Instruções de Build

Nova documentação
> Em 25.11.2024 adicionei RUFF e UV siga o [link](new.md) para verificar.

## Configuração do build:

### Libs e versões usadas no projeto:

|               | Versão | Site                                   |
|---------------|--------|----------------------------------------|
| Python        | 3.10   | https://www.python.org/downloads/


| Lib                 | Versão       | Site                                 |
|---------------------|--------------|--------------------------------------|
| PyQt5               | 5.15.9       |                                      |
| SQLAlchemy          | 2.0.5.post1  |                                      |
| pyinstaller         | 5.8.0        |                                      |
| moment              | 0.12.1       |                                      |
| openpyxl            | 3.1.1        |                                      |
| darkdetect          | 0.8.0        | https://pypi.org/project/darkdetect/ |


Instalar as libs acima com o comando 

```
pip install PyQt5 SQLALchemy pyinstaller moment openpyxl darkdetect
```
ou alternativamente usar 
```
pip install -r requirements.txt
```

## Localização dos icones:

Os icones foram pegos desta coleção, provavelmente irão mudar no futuro.

https://iconarchive.com/show/farm-fresh-icons-by-fatcow.html

Download aqui 👇

https://github.com/gammasoft/fatcow

https://fatcow.com/free-icons 


## Para executar o programa

```
python src/main.py
```

Opções de linhas de comando:

| Comando            | Opt1    | Opt2   |   Descrição                                                                           |
|--------------------|---------|--------|----------------------------------------------------------------------------|
| python src/main.py | -h | --help   | mostra opções de chamada de linha de comando                                        |
| python src/main.py | -d | --drop   | Elimina dados da base de dados                                                      |
| python src/main.py | -s | --sample | Adiciona dados de exemplo na base de dados.                                         |
| python src/main.py | -o CONTA_ID | --conta CONTA_ID | Ao iniciar abre a conta com o ID indicado, se ela existir.  |
| python src/main.py | -T THEME | --theme THEME | Nome do diretório do tema dentro de ./themes/\<THEME\>.   |


## Como gerar o executavel

Dentro do diretório scripts existem 2 arquivos, para windows e linux respectivamente

### Windows
Criar um .exe que contem todas as libs (recomendado). 
```
build-onefile.bat
```

Criar um .exe menor e manter as libs separadamente
```
build-onedir.bat
```

### Linux
```
build.sh
```

o executavel será gerado no diretório ```/dist```

# Possíveis problemas

## Instalar locale do Portugues Brasil - no linux

Verificar se existe ``` pt_BR ``` na lista de locales:
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
