import os
import sys
import subprocess
import venv

# Caminhos
if sys.platform == "win32":
    python_venv = os.path.join("venv", "Scripts", "python.exe")
    pip_venv = os.path.join("venv", "Scripts", "pip.exe")
else:
    python_venv = os.path.join("venv", "bin", "python")
    pip_venv = os.path.join("venv", "bin", "pip")

def executar(comando):
    print(f"\n[Executando]: {' '.join(comando)}")
    resultado = subprocess.run(comando)
    if resultado.returncode != 0:
        print(f"[Erro] Falha ao executar: {' '.join(comando)}")
        sys.exit(1)

def main():
    print("Processo de configuração e inicialização iniciando...")

    # 1. Cria o ambiente virtual
    if not os.path.exists("venv"):
        print("Criando o ambiente virtual...")
        venv.create("venv", with_pip=True)
    else:
        print("Ambiente virtual 'venv' já existe.")

    # 2. Instala as dependências listadas
    if os.path.exists("requirements.txt"):
        executar([pip_venv, "install", "-r", "requirements.txt"])
    else:
        print("[Aviso] requirements.txt não encontrado. Instalando pacotes básicos...")
        executar([pip_venv, "install", "django", "dj-database-url"])

    # Garante o dj-database-url caso tenha sido esquecido no requirements.txt
    executar([pip_venv, "install", "dj-database-url"])

    # 3. Aplica as migrações do Django
    executar([python_venv, "manage.py", "makemigrations"])
    executar([python_venv, "manage.py", "migrate"])

    # 4. Popula o banco de dados
    if os.path.exists("popular_banco.py"):
        executar([python_venv, "popular_banco.py"])

    # 5. Coleta os arquivos estáticos
    executar([python_venv, "manage.py", "collectstatic", "--noinput"])

    print("\nConfiguração concluída! Abrindo o servidor em http://127.0.0.1:8080 ...")

    # 6. Inicia o servidor usando o Python do venv
    try:
        subprocess.run([python_venv, "manage.py", "runserver", "8080"])
    except KeyboardInterrupt:
        print("\nServidor encerrado.")

if __name__ == "__main__":
    main()