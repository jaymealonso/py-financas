
del dist\py-financas.exe /Q
rmdir dist\themes /S /Q

pyinstaller src\main.py ^
--name py-financas ^
--onefile ^
--noconfirm ^
--paths src\view\icons ^
--add-data "src/view/icons/*.png;view/icons/" ^
--noconsole ^
--icon="src\view\icons\app-icon.ico"
@REM "src\view\icons\app-icon-32.png"

xcopy themes dist\themes /S /Y /I