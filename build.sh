#!/usr/bin/bash

pyinstaller src/main.py \ 
--name py-financas \
--onefile --noconfirm \
--paths src/view/icons \
--add-data "src/view/icons/*.png:view/icons/"

# --splash "./src/imagens/splash.png"

# pyinstaller src/main.py --name py-financas --onefile \
#     --hidden-import src/view/icons/icons.py