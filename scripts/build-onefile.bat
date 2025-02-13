
del dist\py-financas.exe /Q
rmdir dist\themes /S /Q

xcopy themes dist\themes /S /Y /I

pyinstaller src\main.py ^
--name py-financas ^
--noconfirm ^
--onefile ^
--paths src\view\icons ^
--collect-submodules=numpy.f2py ^
--collect-submodules=scipy._lib.array_api_compat.numpy.fft ^
--noconsole ^
--add-data "src/view/icons/*.png;view/icons/" ^
--icon="src\view\icons\app-icon.ico"


@REM --noconsole ^

@REM --splash "src\imagens\splash.png"

@REM--hiddenimport=scipy._lib.array_api_compat.numpy.fft ^

@REM --icon="src\view\icons\app-icon.ico" ^
@REM --add-data "src/imagens/*.png;imagens/" ^
@REM "src\view\icons\app-icon-32.png"