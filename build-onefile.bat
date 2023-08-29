
del dist\py-financas.exe /Q
rmdir dist\themes /S /Q

pyinstaller src\main.py ^
--name py-financas ^
--noconfirm ^
--onefile ^
--paths src\view\icons ^
--noconsole ^
--add-data "src/view/icons/*.png;view/icons/" ^
--icon="src\view\icons\app-icon.ico" ^
--splash "src\imagens\splash.png"

@REM --add-data "src/imagens/*.png;imagens/" ^

@REM "src\view\icons\app-icon-32.png"

xcopy themes dist\themes /S /Y /I