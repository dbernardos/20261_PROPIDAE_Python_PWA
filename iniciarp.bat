@echo off
chcp 65001 >nul

:: Verifica especificamente se o Python 3.14 esta disponivel via launcher 'py'
py -3.14 --version >nul 2>&1
if errorlevel 1 (
    echo Python 3.14 nao encontrado. Instalando via winget...
    winget install --id Python.Python.3.14 -e --source winget --accept-package-agreements --accept-source-agreements
    
    if errorlevel 1 (
        echo [ERRO] Falha ao instalar o Python 3.14 via winget.
        pause
        exit /b 1
    )

    :: Atualiza o PATH na sessao atual (incluindo o novo caminho do Python Install Manager)
    for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "UserPath=%%b"
    for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "SysPath=%%b"
    set "PATH=%SysPath%;%UserPath%;%LocalAppData%\Python\bin"
)

::  Pergunta a porta
set /p porta="Digite a porta (pressione Enter para 8000): "
if "%porta%"=="" set porta=8000

:: Executa o start.py chamando explicitamente o Python 3.14
echo Preparando ambiente virtual, dependencias e banco de dados...
py -3.14 start.py --no-server

if errorlevel 1 (
    echo.
    echo [ERRO] Falha durante a configuracao no start.py.
    pause
    exit /b 1
)

:: Inicia o servidor na porta escolhida
echo.
echo Iniciando o Django na porta %porta%...
powershell -NoExit -ExecutionPolicy Bypass -Command "& { .\venv\Scripts\Activate.ps1; python manage.py runserver %porta% }"
