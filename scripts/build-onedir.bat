
del dist\py-financas.exe /Q
rmdir dist\themes /S /Q
rmdir dist /S /Q

pyinstaller src\main.py ^
--name py-financas ^
--noconfirm ^
--paths src\view\icons ^
--noconsole ^
--add-data "src/view/icons/*.png;view/icons/" ^
--add-data "src/imagens/*.png;imagens/" ^
--icon="src\view\icons\app-icon.ico"

@REM "src\view\icons\app-icon-32.png"

xcopy themes dist\py-financas\themes /S /Y /I