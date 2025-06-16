uvx pyinstaller src\main.py ^
--name py-financas ^
--noconfirm ^
--onefile ^
--paths src\view\icons ^
--collect-submodules=numpy.f2py ^
--collect-submodules=scipy._lib.array_api_compat.numpy.fft ^
--noconsole ^
--add-data "src/view/icons/*.png;view/icons/" ^
--icon="src\view\icons\app-icon.ico"
