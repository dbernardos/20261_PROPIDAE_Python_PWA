@echo off

set /p porta="Digite a porta (pressione Enter para 8000): "
if "%porta%"=="" set porta=8000

python setup.py

echo Iniciando o Django na porta %porta%...
powershell -NoExit -ExecutionPolicy Bypass -Command "& {.\venv\Scripts\Activate.ps1; python manage.py runserver %porta%}"
