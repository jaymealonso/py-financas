# Adição de RUFF e UV
Em 25.11.2024 adicionei utilização de [RUFF](https://docs.astral.sh/ruff/) e [UV](https://github.com/astral-sh/uv) para adicionar funcionalidadeds de adminitração de bibliotecas e versão do python.

# Instruções para instalação usando as novas ferramentas

## Instalar UV
Para instalar uv usando pip execute o seguinte comando ou siga o [link](https://github.com/astral-sh/uv?tab=readme-ov-file#installation) para outros metodos.

With pip.
```
pip install uv
```

## Criar venv
```terminal
uv venv .venv
```


## Instalar Libs
```terminal
uv pip install -r .\pyproject.toml
```

## Executar

```terminal
uv run .\src\main.py
```

## Build 

O build ainda usa o mesmo script com o pyinstaller do documento antigo.

