# 🎓 SEA Eventos - Sistema de Eventos Acadêmicos

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.x%2B-092E20.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

O **SEA Eventos** é um sistema web para gerenciamento de eventos acadêmicos, desenvolvido com o framework Django. O projeto visa facilitar a organização, inscrição, participação e engajamento dos participantes por meio de funcionalidades interativas como quizzes, sorteios e geração de crachás.

---

## 🚀 Funcionalidades

O sistema é composto por 3 aplicações principais (`evento`, `login` e `quiz`) e oferece os seguintes módulos:

- 📅 **Gestão de Eventos e Atividades**
- 📝 **Inscrições**
- 📱 **Leitor de QR Code**
- 🪪 **Geração de Crachás**
- 🧠 **Quiz de Desafios**
- 🎁 **Sorteio de Brindes**
- ✅ **Testes de Software**

---

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python, Django
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Banco de Dados**: SQLite (desenvolvimento)
- **Funcionalidades Adicionais**: Django PWA, Django Smart Selects, Pillow
- **Túnel Seguro**: Ngrok (para exposição local e testes em dispositivos móveis)

---

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado em sua máquina:
- [Python 3.10+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)
- [Ngrok](https://ngrok.com/) (opcional, para testes de tunneling em servidor local)

---

## ⚙️ Instalação e Configuração

Siga os passos abaixo para configurar o ambiente de desenvolvimento localmente:

### 0. Execute todos os processos abaixo de uma vez
```bash
.\iniciar.bat
```
### 1. Execute todos os processos abaixo de uma vez (se já estiver dentro do venv)
```bash
python setup.py
```

### Se quiser fazer manualmente, execute os códigos passo a passo abaixo

### 2. Crie o ambiente virtual
```bash
python -m venv venv
```
### 3. Libere a política de execução de scripts (Windows)
```bash
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope CurrentUser
```
### 4. Ative o ambiente virtual
```bash
venv\Scripts\activate.ps1
```
### 5. Instale as dependências listadas
```bash
pip install -r requirements.txt
```

### 6. Lê as mudanças no banco
```bash
python manage.py makemigrations
```

### 7. efetua as mudanças no banco
```bash
python manage.py migrate
```

### 8. Popule o banco de dados
```bash
python popular_banco.py
```
### 9. Colete os arquivos estáticos
```bash
python manage.py collectstatic
```
### 10. Execute o servidor de desenvolvimento (8000, 8080, depende da sua porta)
```bash
python manage.py runserver
```

## ⚠️ Resolução de Problemas (Troubleshooting)

Caso ocorra algum erro relacionado a pacotes como bootstrap, pwa, django-extensions ou smart-selects, execute a instalação manual das dependências:

```bash
pip install django-bootstrap-v5
pip install django-pwa
pip install django-extensions
pip install django-smart-selects
pip install uuid6
pip install pillow
```

Caso ocorra algum erro na interface de administração do Django, atualize a versão do framework:
```bash
pip install --upgrade django
```

Para remover arquivos indesejados (como arquivos .css) que ficaram presos no cache de versionamento do Git:
```bash
git rm --cached caminho/para/o/arquivo.css
git add .
git commit -m "Remove arquivos estáticos do cache do Git"
git push origin nome-da-branch
```
## Login para admins:
USUARIO: admin_eventos
SENHA: ifsc1234

USUARIO: admin_eventos2
SENHA: ifsc1234

USUARIO: admin_eventos3
SENHA: ifsc1234

## Login para Participantes:
USUARIO: mariana.li
SENHA: participante1


## ACESSO AO SITE:
portalseaeventos.com.br

## Autenticação: 
nome de usuário:ifsc
senha:ifsc
