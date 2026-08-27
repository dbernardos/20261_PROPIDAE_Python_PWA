# 122025PROPIDAEKotlin# 🎓 SEAEvents - Sistema de Eventos Acadêmicos

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.x%2B-092E20.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

O **SEAEvents** é um sistema web completo para gerenciamento de eventos acadêmicos, desenvolvido com o framework Django. O projeto visa facilitar a organização, inscrição, participação e engajamento dos participantes por meio de funcionalidades interativas como quizzes, sorteios e geração de crachás.

---

## 🚀 Funcionalidades

O sistema é composto por 3 aplicações principais (`evento`, `login` e `quiz`) e oferece os seguintes módulos:

- 📅 **Gestão de Eventos e Atividades**: Criação, visualização e gerenciamento de eventos e suas respectivas atividades.
- 📝 **Inscrições**: Sistema fluido para cadastro e inscrição de participantes nas atividades.
- 📱 **Leitor de QR Code**: Validação rápida de presença e credenciais diretamente pelo navegador.
- 🪪 **Geração de Crachás**: Emissão automatizada de crachás personalizados para os participantes.
- 🧠 **Quiz de Desafios**: Módulo interativo onde os participantes podem responder a perguntas e desafios relacionados ao evento.
- 🎁 **Sorteio de Brindes**: Sistema integrado para realizar sorteios aleatórios entre os participantes ativos.
- ✅ **Testes de Software**: Cobertura de testes automatizados para garantir a estabilidade e confiabilidade das funcionalidades.

---

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python, Django
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção - configurável)
- **Funcionalidades Adicionais**: Django PWA (Progressive Web App), Django Smart Selects, UUID6, Pillow (processamento de imagens para crachás)
- **Túnel Seguro**: Ngrok (para exposição local e testes em dispositivos móveis)

---

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado em sua máquina:
- [Python 3.10+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)
- [Ngrok](https://ngrok.com/) (opcional, para testes de tunneling)

---

## ⚙️ Instalação e Configuração

Siga os passos abaixo para configurar o ambiente de desenvolvimento localmente:

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/seaevents.git
cd seaevents