@echo off
chcp 65001 >nul

set /p porta="Digite a porta (pressione Enter para 8000): "
if "%porta%"=="" set porta=8000

echo Preparando ambiente virtual, dependencias e banco de dados...
python start.py --no-server

if errorlevel 1 (
    echo.
    echo [ERRO] Falha durante a configuracao no start.py.
    pause
    exit /b 1
)

echo.
echo Iniciando o Django na porta %porta%...
powershell -NoExit -ExecutionPolicy Bypass -Command "& { .\venv\Scripts\Activate.ps1; python manage.py runserver %porta% }"