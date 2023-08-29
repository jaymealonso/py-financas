
@REM del dist\py-financas.exe /Q
@REM rmdir dist\themes /S /Q
@REM rmdir dist /S /Q

pyinstaller src\main.py ^
--name py-financas ^
--noconfirm ^
--paths src\view\icons ^
--noconsole ^
--add-data "src/view/icons/*.png;view/icons/" ^
--add-data "src/imagens/*.png;imagens/" ^
--icon="src\view\icons\app-icon.ico"

@REM "src\view\icons\app-icon-32.png"

@REM xcopy themes dist\py-financas\themes /S /Y /I