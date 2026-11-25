@echo off
chcp 65001 >nul

:: 1. Verifica se o Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo Python nao encontrado. Instalando via winget...
    winget install --id Python.Python.3.14.3 -e --source winget --accept-package-agreements --accept-source-agreements
    
    if errorlevel 1 (
        echo [ERRO] Falha ao instalar o Python via winget. Instale manualmente em python.org.
        pause
        exit /b 1
    )

    :: Atualiza o PATH na sessao atual para reconhecer o Python sem fechar o terminal
    for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "UserPath=%%b"
    for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "SysPath=%%b"
    set "PATH=%SysPath%;%UserPath%"
)

:: 2. Pergunta a porta
set /p porta="Digite a porta (pressione Enter para 8000): "
if "%porta%"=="" set porta=8000

:: 3. Executa a configuracao sem iniciar o servidor dentro do Python
echo Preparando ambiente virtual, dependencias e banco de dados...
python start.py --no-server

if errorlevel 1 (
    echo.
    echo [ERRO] Falha durante a configuracao no start.py.
    pause
    exit /b 1
)

:: 4. Inicia o servidor na porta escolhida
echo.
echo Iniciando o Django na porta %porta%...
powershell -NoExit -ExecutionPolicy Bypass -Command "& { .\venv\Scripts\Activate.ps1; python manage.py runserver %porta% }"
