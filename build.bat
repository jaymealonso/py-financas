

pyinstaller src\main.py ^
--name py-financas ^
--onefile ^
--noconfirm ^
--paths src\view\icons ^
--add-data "src/view/icons/*.png;view/icons/"
@REM "src\view\icons\app-icon-32.png"
