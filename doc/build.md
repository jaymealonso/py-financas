
# Instruções de Build

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

## Localização dos icones:

Os icones foram pegos desta coleção, provavelmente irão mudar no futuro.

https://iconarchive.com/show/farm-fresh-icons-by-fatcow.html


## Para executar o programa

```
python src/main.py
```

## Como gerar o executavel

### Windows
```
build.bat
```

### Linux
```
build.sh
```

o executavel será gerado no diretório ```/dist```

# Possíveis problemas

## Instalar locale do Portugues Brasil - no lixux

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
