
del dist\py-financas.exe /Q

pyinstaller src\main.py ^
--clean ^
--name py-financas ^
--noconfirm ^
--onefile ^
--paths src\view\icons ^
--noconsole ^
--add-data "src/view/icons/*.png;view/icons/" ^
--icon="src\view\icons\app-icon.ico"

rmdir dist\themes /S /Q
xcopy themes dist\themes /S /Y /I


@REM --collect-submodules=numpy.f2py ^
@REM --collect-submodules=scipy._lib.array_api_compat.numpy.fft ^

@REM --splash "src\imagens\splash.png" ^

@REM--hiddenimport=scipy._lib.array_api_compat.numpy.fft ^

@REM --icon="src\view\icons\app-icon.ico" ^
@REM --add-data "src/imagens/*.png;imagens/" ^
@REM "src\view\icons\app-icon-32.png"