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
    print("Processo de configuração e inicialização iniciando...")

    print(f"\n[Executando]: {' '.join(comando)}")
    resultado = subprocess.run(comando)
    if resultado.returncode != 0:
        print(f"[Erro] Falha ao executar: {' '.join(comando)}")
        sys.exit(1)

def main():
    
    # 1. Cria o ambiente virtual
    if not os.path.exists("venv"):
        print("Criando o ambiente virtual...")
        venv.create("venv", with_pip=True)
    else:
        print("Ambiente virtual 'venv' já existe.")

    # 4. Instala as dependências listadas
    if os.path.exists("requirements.txt"):
        executar([pip_venv, "install", "-r", "requirements.txt"])
    else:
        print("[Aviso] requirements.txt não encontrado. Instalando Django básico...")
        executar([pip_venv, "install", "django"])

    # aplica as migrações do Django
    executar([python_venv, "manage.py", "makemigrations"])
    executar([python_venv, "manage.py", "migrate"])

    # 5. Popula o banco de dados
    if os.path.exists("popular_banco.py"):
        executar([python_venv, "popular_banco.py"])

    # 6. Colete os arquivos estáticos (com --noinput para não travar no terminal)
    executar([python_venv, "manage.py", "collectstatic", "--noinput"])

    print("Processo de configuração e inicialização concluída com sucesso!")

if __name__ == "__main__":
    main()